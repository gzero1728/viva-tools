import { useState } from "react";
import {
  Button,
  Container,
  Paper,
  Typography,
  CircularProgress,
  Box,
  TextField,
} from "@mui/material";
import api from "./lib/axios";

interface ExcelFile {
  content: string;
  filename: string;
}

interface ApiResponse {
  success: boolean;
  data?: any;
  error?: string;
  excel_file?: ExcelFile;
}

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<ApiResponse | null>(null);
  const [itemColIdx, setItemColIdx] = useState<number>(1);
  const [resultColIdx, setResultColIdx] = useState<number>(2);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFile(event.target.files[0]);
    }
  };

  const base64ToBlob = (
    base64: string,
    type: string = "application/octet-stream"
  ): Blob => {
    const binStr = atob(base64);
    const len = binStr.length;
    const arr = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
      arr[i] = binStr.charCodeAt(i);
    }
    return new Blob([arr], { type });
  };

  const downloadBlob = (blob: Blob, filename: string): void => {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  };

  const handleSubmit = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("pdf_file", file);
    formData.append("item_col_idx", itemColIdx.toString());
    formData.append("result_col_idx", resultColIdx.toString());

    setLoading(true);
    try {
      const response = await api.post<ApiResponse>("/extract", formData);
      setResult(response.data);

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
      setResult({
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      });
    }
    setLoading(false);
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          검진결과PDF 데이터 추출
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
