from langchain_community.document_loaders import PyMuPDFLoader
import pdfplumber
import pandas as pd
import openpyxl
import re


def extract_from_pymu(pdf_path):
    loader = PyMuPDFLoader(pdf_path)
    documents = loader.load()
    return documents

def remove_duplicated_chars(text):
    if not text:
        return text
        
    # 특수문자 패턴 정의
    special_chars = r'[,.<>{}[\]\/\\\(\)!@#$%^&*+=|;:"\']'
    
    # 연속된 특수문자 제거
    text = re.sub(f'{special_chars}+', lambda m: m.group()[0], text)
    
    result = []
    prev_char = None
    
    for char in text:
        # 한글인 경우: 이전 문자와 다를 때만 추가
        if re.match('[가-힣]', char):
            if char != prev_char:
                result.append(char)
        # 한글이 아닌 경우: 그대로 추가
        else:
            result.append(char)
        prev_char = char if re.match('[가-힣]', char) else None
    
    # 결과 문자열의 앞뒤 공백 제거
    return ''.join(result).strip()


def extract_from_pdfplumber(pdf_path, item_col_idx=0, result_col_idx=1):
    """
    PDF 테이블 데이터를 파싱하여 검사항목과 결과를 매핑한 리스트를 반환합니다.
    
    Args:
        pdf_path: PDF 파일 경로
        item_col_idx: 검사항목 컬럼의 인덱스 (기본값: 0)
        result_col_idx: 검사결과 컬럼의 인덱스 (기본값: 1)
    
    Returns:
        List[Dict]: 검사항목과 결과가 매핑된 딕셔너리 리스트
    """
    results = []
    
    with pdfplumber.open(pdf_path) as pdf:
        # 모든 페이지를 순회
        for page in pdf.pages:
            tables = page.extract_tables()
            print("tables", tables)
            
            # 페이지 내의 모든 테이블을 순회
            for table in tables:
                # 각 테이블의 행을 순회
                for row in table:
                    # None 값을 필터링한 새로운 row 생성
                    filtered_row = [col for col in row if col is not None]
                    
                    # 필터링된 row의 길이가 부족한 경우 빈 문자열로 확장
                    max_idx = max(item_col_idx, result_col_idx)
                    while len(filtered_row) <= max_idx:
                        filtered_row.append("")
                    
                    item = filtered_row[item_col_idx].strip() if filtered_row[item_col_idx] else ""
                    result = filtered_row[result_col_idx].strip() if filtered_row[result_col_idx] else ""

                    # 한글 중복 문자 제거
                    item = remove_duplicated_chars(item)
                    result = remove_duplicated_chars(result)
                    
                    if item or result:  # 둘 중 하나라도 값이 있으면 추가
                        results.append({
                            "검사항목": item,
                            "검사결과": result
                        })

    """ df = pd.DataFrame(results)
    output_path = pdf_path.rsplit('.', 1)[0] + '_results.xlsx'
    df.to_excel(output_path, index=False) """

    return results

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

