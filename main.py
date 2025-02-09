from src.extract_4llm_to_excel import extract_pdf_data, create_template_excel
from src.extract_from_pymu import extract_from_pymu, format_pymu_data, extract_from_pdfplumber


def main():
    pdf_path = 'src/data/안검진결과1.pdf'
    template_path = 'src/data/template.xlsx'
    
    # 사용자로부터 열 인덱스 입력받기
    try:
        # column_count = int(input("테이블 컬럼의 총 개수를 입력해주세요: "))
        # item_col_idx = int(input("검사항목이 있는 열의 번호를 입력하세요 (0부터 시작): "))
        # result_col_idx = int(input("검사결과가 있는 열의 번호를 입력하세요 (0부터 시작): "))

        # result = extract_pdf_data(pdf_path, item_col_idx, result_col_idx)
        result = extract_from_pdfplumber(pdf_path, 0, 1)
        print('추출된 데이터:\n', result)

    except Exception as e:
        print(f"오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main()