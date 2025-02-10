from langchain_community.document_loaders import PyMuPDFLoader
import pdfplumber
import pandas as pd
import openpyxl
import re
from src.extract_4llm_to_excel import normalize_text
from fuzzywuzzy import fuzz


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
                    # filtered_row = [col for col in row if col is not None]
                    
                    # 필터링된 row의 길이가 부족한 경우 빈 문자열로 확장
                    max_idx = max(item_col_idx, result_col_idx)
                    while len(row) <= max_idx:
                        row.append("")
                    
                    item = row[item_col_idx].strip() if row[item_col_idx] else ""
                    result = row[result_col_idx].strip() if row[result_col_idx] else ""

                    # 한글 중복 문자 제거
                    item = remove_duplicated_chars(item)
                    result = remove_duplicated_chars(result)
                    
                    if item or result:  # 둘 중 하나라도 값이 있으면 추가
                        results.append({
                            "검사항목": item,
                            "검사결과": result
                        })

    df = pd.DataFrame(results)
    output_path = pdf_path.rsplit('.', 1)[0] + '_1_results.xlsx'
    df.to_excel(output_path, index=False)

    return results

def extract_from_pdfplumber2(pdf_path, item_col_name="검사항목", result_col_name="검사결과"):
    """
    PDF 테이블 데이터를 파싱하여 검사항목과 결과를 매핑한 리스트를 반환합니다.
    
    Args:
        pdf_path: PDF 파일 경로
        item_col_name: 검사항목 컬럼의 이름 (기본값: "검사항목")
        result_col_name: 검사결과 컬럼의 이름 (기본값: "검사결과")
    
    Returns:
        List[Dict]: 검사항목과 결과가 매핑된 딕셔너리 리스트
    """
    results = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            
            for table in tables:
                if not table:
                    continue
                
                # 헤더 행과 인덱스 찾기
                header_row_idx = None
                item_col_idx = 0
                result_col_idx = 1
                
                for row_idx, row in enumerate(table):
                    if not row:
                        continue
                    
                     # 중복 문자 제거
                    filtered_row = [
                        remove_duplicated_chars(col.strip()) if col else ""
                        for col in row
                    ]

                    print("filtered_row", filtered_row)

                    # 현재 행에서 컬럼 이름 찾기
                    try:
                        item_idx = filtered_row.index(item_col_name)
                        result_idx = filtered_row.index(result_col_name)
                        header_row_idx = row_idx
                        item_col_idx = item_idx
                        result_col_idx = result_idx
                        break
                    except ValueError:
                        continue
                
                # 데이터 처리 시작 행 결정
                start_row = header_row_idx + 1 if header_row_idx is not None else 0
                
                # 데이터 행 처리
                for row in table[start_row:]:
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
                            item_col_name: item,
                            result_col_name: result
                        })
                        
    df = pd.DataFrame(results)
    output_path = pdf_path.rsplit('.', 1)[0] + '_results2.xlsx'
    df.to_excel(output_path, index=False)

    return results

def extract_from_pdfplumber3(pdf_path, item_col_idx=0, result_col_idx=1, template_path='template.xlsx'):
    """
    PDF 테이블 데이터를 파싱하여 검사항목과 결과를 매핑한 리스트를 반환합니다.
    
    Args:
        pdf_path: PDF 파일 경로
        item_col_idx: 검사항목 컬럼의 인덱스 (기본값: 0)
        result_col_idx: 검사결과 컬럼의 인덱스 (기본값: 1)
        template_path: 템플릿 엑셀 파일 경로
    """
    # 템플릿 엑셀 파일 로드
    template_df = pd.read_excel(template_path)
    
    results = []
    total_items = 0
    exact_matches = 0
    fuzzy_matches = 0
    failed_matches = 0
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables()
            
            if not tables:
                # 테이블이 없는 경우 텍스트 추출
                text = page.extract_text()
                if text:
                    results.append({
                        "페이지": page_num,
                        "검사항목": "",
                        "검사결과": text.strip(),
                        "CH검사명": "",
                        "CH코드": "",
                        "유사도": 0
                    })
                continue
                
            for table in tables:
                for row in table:
                    max_idx = max(item_col_idx, result_col_idx)
                    while len(row) <= max_idx + 1:
                        row.append("")
                    
                    item = row[item_col_idx].strip() if row[item_col_idx] else ""
                    result = row[result_col_idx].strip() if row[result_col_idx] else ""
                    
                    # result가 None인 경우 다음 컬럼 확인
                    if not result and result_col_idx + 1 < len(row):
                        result = row[result_col_idx + 1].strip() if row[result_col_idx + 1] else ""
                    
                    # 한글 중복 문자 제거
                    item = remove_duplicated_chars(item)
                    result = remove_duplicated_chars(result)

                    if item or result:
                        total_items += 1
                        matched = False
                        matched_header = ""
                        matched_value = ""
                        similarity = 0
                        
                        if item:
                            # 검사항목 정규화
                            search_item = normalize_text(item)

                            # 정확한 매칭 시도
                            for col in template_df.columns:
                                col_parts = normalize_text(col)
                                
                                # 영문 약자 매칭 확인
                                search_abbr = {p for p in search_item if p.isascii() and p.isupper()}
                                col_abbr = {p for p in col_parts if p.isascii() and p.isupper()}
                                
                                if (search_abbr and col_abbr and search_abbr & col_abbr) or (search_item & col_parts):
                                    matched = True
                                    matched_header = col
                                    matched_value = template_df[col].iloc[0]
                                    similarity = 100
                                    exact_matches += 1
                                    break
                            
                            # 정확한 매칭이 없는 경우 퍼지 매칭 시도
                            if not matched:
                                similarity_scores = []
                                for col in template_df.columns:
                                    max_score = max(
                                        max(fuzz.ratio(s1, s2) for s2 in normalize_text(col))
                                        for s1 in search_item
                                    )
                                    similarity_scores.append((col, max_score))
                                
                                best_match = max(similarity_scores, key=lambda x: x[1])
                                if best_match[1] >= 80:
                                    matched_header = best_match[0]
                                    matched_value = template_df[best_match[0]].iloc[0]
                                    similarity = best_match[1]
                                    fuzzy_matches += 1
                                else:
                                    failed_matches += 1
                        
                        results.append({
                            "페이지": page_num,
                            "검사항목": item,
                            "검사결과": result,
                            "CH검사명": matched_header,
                            "CH코드": matched_value,
                            "유사도": similarity
                        })

    # 매칭 통계 출력
    print("\n=== 매칭 결과 통계 ===")
    print(f"총 검사항목 개수: {total_items}")
    print(f"정확히 매칭된 항목: {exact_matches} ({(exact_matches/total_items*100):.1f}%)")
    print(f"퍼지 매칭 성공 항목: {fuzzy_matches} ({(fuzzy_matches/total_items*100):.1f}%)")
    print(f"매칭 실패 항목: {failed_matches} ({(failed_matches/total_items*100):.1f}%)")
    print("==================")

    # DataFrame 생성 및 저장
    df = pd.DataFrame(results)
    
    # 엑셀 파일로 저장 (스타일링 적용)
    output_path = pdf_path.rsplit('.', 1)[0] + '_3_results.xlsx'
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        
        # 스타일링 적용
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        
        # 유사도가 80% 미만인 행에 녹색 배경 적용
        for idx, row in df.iterrows():
            if row['유사도'] < 80:
                for col in range(1, len(df.columns) + 1):
                    cell = worksheet.cell(row=idx + 2, column=col)
                    cell.fill = openpyxl.styles.PatternFill(start_color="90EE90", end_color="90EE90", fill_type="solid")
    df.to_excel(output_path, index=False)

    return results