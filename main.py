from src.pdf_to_excel import extract_pdf_data, create_template_excel
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import PDFMinerPDFasHTMLLoader
from bs4 import BeautifulSoup
import re


def extract_table_data(pdf_path, item_col_idx, result_col_idx):
    """
    PDF 파일에서 표 데이터를 추출하는 함수
    
    Args:
        pdf_path (str): PDF 파일 경로
        item_col_idx (int): 검사항목이 있는 열의 인덱스
        result_col_idx (int): 검사결과가 있는 열의 인덱스
    
    Returns:
        list: 추출된 데이터 리스트
    """
    loader = PyMuPDFLoader(pdf_path)
    pages = loader.load()
    print('pages', pages)
    result_data = []

    for page in pages:
        # 페이지 내용을 줄 단위로 분리
        lines = page.page_content.split('\n')
        
        for line in lines:
            # 각 줄을 공백을 기준으로 분리하여 열로 만듦
            columns = [col.strip() for col in line.split('  ') if col.strip()]
            
            # 행이 충분한 열을 가지고 있는지 확인
            max_idx = max(item_col_idx, result_col_idx)
            if len(columns) > max_idx:
                item = columns[item_col_idx]
                result = columns[result_col_idx]
                
                # 빈 셀이나 의미 없는 데이터 제외
                if item and not item.startswith('('):
                    result_data.append({
                        "검사항목": item,
                        "검사결과": result
                    })
    
    return result_data

def extract_data_to_html(pdf_path, item_col_idx, result_col_idx):
    """
    PDF를 HTML로 변환하고 테이블 데이터를 추출하는 함수
    
    Args:
        pdf_path (str): PDF 파일 경로
        item_col_idx (int): 검사항목이 있는 열의 인덱스
        result_col_idx (int): 검사결과가 있는 열의 인덱스
    
    Returns:
        list: 추출된 데이터 리스트
    """
    loader = PDFMinerPDFasHTMLLoader(pdf_path)
    docs = loader.load()
    
    # HTML 파싱
    soup = BeautifulSoup(docs[0].page_content, 'html.parser')
    
    # 결과를 저장할 리스트
    result_data = []
    
    # 모든 텍스트 라인을 찾음
    text_elements = soup.find_all(['div', 'span'])
    
    for element in text_elements:
        text = element.get_text().strip()
        if text:
            # 연속된 공백을 하나의 공백으로 변환
            text = re.sub(r'\s+', ' ', text)
            columns = text.split(' ')
            
            # 행이 충분한 열을 가지고 있는지 확인
            max_idx = max(item_col_idx, result_col_idx)
            if len(columns) > max_idx:
                item = columns[item_col_idx].strip()
                result = columns[result_col_idx].strip()
                
                # 빈 셀이나 의미 없는 데이터 제외
                if item and not item.startswith('('):
                    result_data.append({
                        "검사항목": item,
                        "검사결과": result
                    })
    
    print('추출된 데이터:', result_data)
    return result_data

def main():
    pdf_path = 'src/data/검진결과2.pdf'
    output_path = 'src/data/20241227_1.xlsx'
    template_path = 'src/data/template.xlsx'
    
    # 사용자로부터 열 인덱스 입력받기
    try:
        item_col_idx = int(input("검사항목이 있는 열의 번호를 입력하세요 (0부터 시작): "))
        result_col_idx = int(input("검사결과가 있는 열의 번호를 입력하세요 (0부터 시작): "))
        
        # 표 데이터 추출
        """ table_data = extract_table_data(pdf_path, item_col_idx, result_col_idx)
        print('추출된 데이터:', table_data) """

        # 기존 로직 유지
        """ extracted_data = extract_pdf_data(pdf_path)
        create_template_excel(template_path, extracted_data) """

        table_data = extract_data_to_html(pdf_path, item_col_idx, result_col_idx)
        print('추출된 데이터:', table_data)

    except Exception as e:
        print(f"오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main()