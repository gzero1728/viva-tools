import pymupdf4llm
from langchain_community.document_loaders import PyPDFLoader
import pandas as pd
from fuzzywuzzy import fuzz

def extract_pdf_data(pdf_path):
    try:
    # 표 데이터 추출 (pymupdf4llm 사용)
        table_content = pymupdf4llm.to_markdown(pdf_path)
        print('table_content', table_content)
        

        # 마크다운 테이블을 파싱하여 필요한 데이터만 추출
        extracted_data = []
        
        # 테이블 문자열을 줄 단위로 분리
        lines = table_content.strip().split('\n')
        
        # 헤더 행과 구분자 행을 건너뛰고 데이터 행만 처리
        for line in lines:
            if line.startswith('|') and not line.startswith('|-'):
                # 각 열 데이터를 분리하고 공백 제거
                columns = [col.strip() for col in line.split('|')]
                # 빈 문자열 제거
                columns = [col for col in columns if col]
                
                if len(columns) >= 3:  # 최소 3개 열이 있는지 확인
                    # 검사항목(1열)과 검사결과값(3열)만 추출
                    item = columns[0]
                    result = columns[-1]
                    extracted_data.append({
                        "검사항목": item,
                        "검사결과": result
                    })
        return extracted_data
       
        
    except Exception as e:
        print(f"PDF 처리 중 오류 발생: {str(e)}")
        return None
    

KOR_ENG_MAPPING = {
    '유로빌리노겐': 'urobilinogen',
    '빌리루빈': 'bilirubin',
    '케톤체': 'ketone',
    '아질산염': 'nitrite',
    '백혈구': 'wbc',
    '적혈구': 'rbc',
    '혈색소': 'hb',
    '호중구': ['neutrophil', 'neutroph'],
    '요비중': ['specific gravity', 'sg', 's.g'],
    # 필요한 매핑을 더 추가할 수 있습니다
}
    

def normalize_text(text):
    """텍스트 정규화: 괄호 처리, 순서 통일, 한영 변환"""
    import re
    
    # 소문자로 변환
    text = text.lower()
    
    # 점(.) 제거하여 약어 통일 (예: s.g -> sg)
    text = text.replace('.', '')
    
    # 괄호 안의 텍스트 추출 (영문 약자 우선 처리)
    abbreviations = re.findall(r'\(([A-Za-z0-9]+)\)', text)
    # 나머지 괄호 내용 추출
    other_brackets = [b for b in re.findall(r'\((.*?)\)', text) if b not in abbreviations]
    
    # 괄호 제거한 기본 텍스트
    base_text = re.sub(r'[\(\)]', '', text).strip()
    
    # 슬래시로 구분된 텍스트를 분리
    parts = set([p.strip() for p in base_text.split('/')] + abbreviations + other_brackets)
    # 빈 문자열 제거
    parts = set(p for p in parts if p)
    
    # 한글이 있는 경우 영문 매핑 추가
    expanded_parts = set(parts)
    for part in parts:
        # 한글 매핑이 있는 경우 영문 버전 추가
        if part in KOR_ENG_MAPPING:
            mapping = KOR_ENG_MAPPING[part]
            if isinstance(mapping, list):
                expanded_parts.update(mapping)
            else:
                expanded_parts.add(mapping)
        # 영문 매핑이 있는 경우 한글 버전 추가
        for kor, eng in KOR_ENG_MAPPING.items():
            if isinstance(eng, list):
                if part in eng:
                    expanded_parts.add(kor)
            elif part == eng:
                expanded_parts.add(kor)
    
    return expanded_parts



def create_template_excel(template_path, pdf_data):
    try:
        # 템플릿 엑셀 파일 읽기
        template_df = pd.read_excel(template_path)
        pdf_df = pd.DataFrame(pdf_data)

        # 매칭 통계를 위한 카운터 초기화
        total_items = len(pdf_df)
        exact_matches = 0
        fuzzy_matches = 0
        failed_matches = 0
        
        # template_df의 복사본 생성 (원본 데이터 보존)
        result_df = template_df.copy()
    
        for index, row in pdf_df.iterrows():
            try:
                # 검사항목 정규화
                search_item = normalize_text(row['검사항목'])
                
                # 정확한 매칭 먼저 시도
                matched = False
                for col in template_df.columns:
                    col_parts = normalize_text(col)
                    
                    # 영문 약자 매칭 확인
                    search_abbr = {p for p in search_item if p.isascii() and p.isupper()}
                    col_abbr = {p for p in col_parts if p.isascii() and p.isupper()}
                    
                    # 영문 약자가 일치하거나 일반 텍스트 교집합이 있으면 매칭
                    if (search_abbr and col_abbr and search_abbr & col_abbr) or (search_item & col_parts):
                        matching_cols = template_df.columns == col
                        matched = True
                        exact_matches += 1
                        print(f"✅ {row['검사항목']} -> {col}")
                        break

                
               # 정확한 매칭이 없는 경우 퍼지 매칭 시도
                if not matched:
                    # 각 컬럼에 대해 유사도 점수 계산
                    similarity_scores = []
                    for col in template_df.columns:
                        # 각 부분 텍스트끼리의 최대 유사도 계산
                        max_score = max(
                            max(fuzz.ratio(s1, s2) for s2 in normalize_text(col))
                            for s1 in search_item
                        )
                        similarity_scores.append((col, max_score))
                    
                    # 가장 높은 유사도를 가진 매칭 찾기
                    best_match = max(similarity_scores, key=lambda x: x[1])
                    if best_match[1] >= 80:
                        print(f"✅ {row['검사항목']} -> {best_match[0]} (유사도: {best_match[1]}%)")
                        matching_cols = template_df.columns == best_match[0]
                        fuzzy_matches += 1
                    else:
                        print(f"❌ {row['검사항목']}")
                        failed_matches += 1
               

                

            except Exception as e:
                print(f"데이터 매칭 중 오류 발생: {str(e)}, 항목: {row['검사항목']}")

        # 매칭 통계 출력
        print("\n=== 매칭 결과 통계 ===")
        print(f"총 검사항목 개수: {total_items}")
        print(f"정확히 매칭된 항목: {exact_matches} ({(exact_matches/total_items*100):.1f}%)")
        print(f"퍼지 매칭 성공 항목: {fuzzy_matches} ({(fuzzy_matches/total_items*100):.1f}%)")
        print(f"매칭 실패 항목: {failed_matches} ({(failed_matches/total_items*100):.1f}%)")
        print("==================")

        # 결과 엑셀 파일 저장
        """ output_path = template_path.replace('.xlsx', '_result.xlsx')
        result_df.to_excel(output_path, sheet_name="Result", index=False) """
        

  

        return result_df

    except Exception as e:
        print(f"Excel 파일 생성 중 오류 발생: {str(e)}")
        return None
