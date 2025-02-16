import { useState } from "react";
import axios from "axios";
import {
  Button,
  Container,
  Paper,
  Typography,
  CircularProgress,
  Box,
  TextField,
} from "@mui/material";

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [itemColIdx, setItemColIdx] = useState(1);
  const [resultColIdx, setResultColIdx] = useState(2);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("pdf_file", file);
    formData.append("item_col_idx", itemColIdx);
    formData.append("result_col_idx", resultColIdx);

    setLoading(true);
    try {
      const response = await axios.post("/api/extract", formData);
      setResult(response.data);

      // 엑셀 파일 다운로드
      if (response.data.success && response.data.excel_file) {
        const { content, filename } = response.data.excel_file;
        const blob = base64ToBlob(
          content,
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        );
        downloadBlob(blob, filename);
      }
    } catch (error) {
      console.error("Error:", error);
      setResult({ success: false, error: error.message });
    }
    setLoading(false);
  };

  // base64를 Blob으로 변환하는 유틸리티 함수
  const base64ToBlob = (base64, type = "application/octet-stream") => {
    const binStr = atob(base64);
    const len = binStr.length;
    const arr = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
      arr[i] = binStr.charCodeAt(i);
    }
    return new Blob([arr], { type });
  };

  // Blob을 파일로 다운로드하는 유틸리티 함수
  const downloadBlob = (blob, filename) => {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          검진결과 PDF 데이터 추출
        </Typography>

        <Box sx={{ mb: 3 }}>
          <input
            accept="application/pdf"
            type="file"
            onChange={handleFileChange}
            style={{ marginBottom: 20 }}
          />
        </Box>

        <Box sx={{ mb: 3, display: "flex", gap: 2 }}>
          <TextField
            label="검사항목 컬럼 인덱스"
            type="number"
            value={itemColIdx}
            onChange={(e) => setItemColIdx(Number(e.target.value))}
            size="small"
          />
          <TextField
            label="검사결과 컬럼 인덱스"
            type="number"
            value={resultColIdx}
            onChange={(e) => setResultColIdx(Number(e.target.value))}
            size="small"
          />
        </Box>

        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={!file || loading}
        >
          {loading ? <CircularProgress size={24} /> : "파일 업로드"}
        </Button>

        {result && (
          <Paper sx={{ mt: 3, p: 2, bgcolor: "#f5f5f5" }}>
            <Typography variant="h6" gutterBottom>
              결과:
            </Typography>
            <pre style={{ overflow: "auto", maxHeight: "400px" }}>
              {JSON.stringify(result, null, 2)}
            </pre>
          </Paper>
        )}
      </Paper>
    </Container>
  );
}

export default App;
