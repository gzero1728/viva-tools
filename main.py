from src.extract_from_plumber import extract_from_pdfplumber3, extract_from_pdfplumber2

def main():
    pdf_path = 'src/data/검진결과1.pdf'
    template_path = 'src/data/template.xlsx'
    
    try:
        result = extract_from_pdfplumber3(pdf_path, 1, 2, template_path)
        print('추출된 데이터:\n', result)

    except Exception as e:
        print(f"오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main()