import pdfplumber
import pandas as pd

from fuzzywuzzy import fuzz
from .text_normalizer import normalize_text, remove_duplicated_chars

def extract_pdf(pdf_path: str, item_col_idx: int = 0, result_col_idx: int = 1) -> list:
    """
    PDF 테이블 데이터를 파싱하여 검사항목과 결과를 매핑한 리스트를 반환합니다.
    
    Args:
        pdf_path: PDF 파일 경로
        item_col_idx: 검사항목 컬럼의 인덱스 (기본값: 0)
        result_col_idx: 검사결과 컬럼의 인덱스 (기본값: 1)
        template_path: 템플릿 엑셀 파일 경로
    """
    # 템플릿 엑셀 파일 로드
    template_path = 'src/data/template.xlsx'
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

    return results