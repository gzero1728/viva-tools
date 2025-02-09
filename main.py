from src.extract_from_plumber import extract_from_pdfplumber

def main():
    pdf_path = 'src/data/검진결과1.pdf'
    template_path = 'src/data/template.xlsx'
    
    try:
        result = extract_from_pdfplumber(pdf_path, 0, 1)
        print('추출된 데이터:\n', result)

    except Exception as e:
        print(f"오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main()