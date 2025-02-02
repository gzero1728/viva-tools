from src.pdf_to_excel import extract_pdf_data
from src.pdf_to_excel import create_template_excel

def main():
    pdf_path = 'src/data/안긁검진결과1.pdf'
    output_path = 'src/data/20241227_1.xlsx'
    template_path = 'src/data/template.xlsx'

    extracted_data = extract_pdf_data(pdf_path)
    """ print('extracted_data', extracted_data) """

    create_template_excel(template_path, extracted_data)

    


if __name__ == "__main__":
    main()