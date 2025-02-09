from langchain_community.document_loaders import PyMuPDFLoader
import pdfplumber
import pandas as pd
import openpyxl

def extract_from_pymu(pdf_path):
    loader = PyMuPDFLoader(pdf_path)
    documents = loader.load()
    return documents

def extract_from_pdfplumber(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        third_page = pdf.pages[2]
        tables = third_page.extract_tables()
        
    df = pd.DataFrame(tables[1][1:])
    # df.to_excel("sample.xlsx", index=False)
    return df.set_index(0)[1].to_dict()

def format_pymu_data(pdf_path, column_count, item_col_idx, result_col_idx):
    """
    PDF 테이블 데이터를 파싱하여 검사항목과 결과를 매핑한 리스트를 반환합니다.
    
    Args:
        documents: PDF 문서 데이터
        column_count: 테이블의 전체 컬럼 수
        item_col_idx: 검사항목 컬럼의 인덱스 (0부터 시작)
        result_col_idx: 검사결과 컬럼의 인덱스 (0부터 시작)
    
    Returns:
        List[Dict]: 검사항목과 결과가 매핑된 딕셔너리 리스트
    """
    documents = extract_from_pymu(pdf_path)
    results = []
    
    for doc in documents:
        # 각 줄을 컬럼 수로 분할
        lines = doc.page_content.split('\n')
        
        # 각 줄을 컬럼으로 분리하여 처리
        for i in range(0, len(lines), column_count):
            if i + column_count <= len(lines):
                columns = lines[i:i + column_count]
                
                # 검사항목과 결과가 모두 있는 경우만 처리
                if len(columns) > max(item_col_idx, result_col_idx):
                    item = columns[item_col_idx].strip()
                    result = columns[result_col_idx].strip()
                    
                    # 빈 값이 아닌 경우만 추가
                    if item and result:
                        results.append({
                            "검사항목": item,
                            "검사결과": result
                        })
    
    return results

