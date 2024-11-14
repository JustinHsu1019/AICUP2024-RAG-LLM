import zipfile
import pytesseract
from pdf2image import convert_from_bytes
import os
import json

# Configure Tesseract path if necessary (update this path as needed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def ocr_in_folder(zip_path, folder, output_dir):
    """
    Extracts PDF files from a ZIP archive, performs OCR, and saves the output text.

    Args:
        zip_path (str): The path to the ZIP file containing the documents.
        folder (str): The folder path inside the ZIP to search for PDF files.
        output_dir (str): The directory to save the OCR output text files.

    Returns:
        None
    """
    folder_path = f"{folder}/"

    with zipfile.ZipFile(zip_path, 'r') as zipf:
        for zip_info in zipf.infolist():
            if zip_info.filename.startswith(folder_path) and not zip_info.is_dir():
                with zipf.open(zip_info.filename) as pdf_file:
                    pdf_bytes = pdf_file.read()

                    # Specify the path to the Poppler binaries if needed
                    poppler_path = r"C:\Program Files\poppler-24.08.0\Library\bin"
                    
                    # Convert the PDF bytes to images
                    images = convert_from_bytes(pdf_bytes, dpi=300, poppler_path=poppler_path)

                    os.makedirs(output_dir, exist_ok=True)

                    # Extract only the base filename (e.g., "file1.pdf" instead of the full path)
                    base_filename = os.path.basename(zip_info.filename)

                    # Perform OCR on each page and save the text
                    for i, image in enumerate(images):
                        text = pytesseract.image_to_string(image, lang="chi_tra")
                        output_file_path = os.path.join(output_dir, f'{base_filename}_page_{i + 1}.txt')
                        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
                        with open(output_file_path, 'w', encoding='utf-8') as f:
                            f.write(text)
                    print(f"OCR completed for {base_filename}")

# OCR extraction paths
zip_path = 'datazip.zip'
ocr_in_folder(zip_path, "競賽資料集/reference/insurance", 'dataset/output_text/insurance')
ocr_in_folder(zip_path, "競賽資料集/reference/finance", 'dataset/output_text/finance')

# FAQ and OCR JSON processing
import json
import os

# File paths
FAQ_FILEPATH = 'datazip/競賽資料集/reference/faq/pid_map_content.json'
FINANCE_OCR_FOLDER_PATH = 'dataset/output_text/finance'
INSURANCE_OCR_FOLDER_PATH = 'dataset/output_text/insurance'


def check_text(file_path, category):
    """
    Reads a JSON FAQ file, processes it, and returns formatted data.

    Args:
        file_path (str): Path to the FAQ JSON file.
        category (str): Category label for the FAQ data.

    Returns:
        list: A list of dictionaries containing formatted FAQ data.
    """
    formatted_data = []
    with open(file_path, "r", encoding="utf-8") as faq_file:
        loaded_faq = json.load(faq_file)

    for qid, questions in loaded_faq.items():
        for question_item in questions:
            formatted_entry = {
                "category": category,
                "qid": qid,
                "content": {
                    "question": question_item["question"],
                    "answers": question_item["answers"]
                }
            }
            formatted_data.append(formatted_entry)
            print(formatted_entry)
    return formatted_data


def read_ocr_files(ocr_folder_path, category):
    """
    Reads text files generated from OCR, consolidates them, and returns formatted data.

    Args:
        ocr_folder_path (str): Path to the folder containing OCR text files.
        category (str): Category label for the OCR data.

    Returns:
        list: A list of dictionaries containing consolidated OCR data.
    """
    formatted_data = []

    # Capture the name of file
    file_basenames = set()
    for filename in os.listdir(ocr_folder_path):
        if filename.endswith('.txt'):
            basename = filename.split('.pdf_page_')[0]
            file_basenames.add(basename)

    for basename in sorted(file_basenames, key=lambda x: int(x)):
        all_text = ""
        page_files = []

        for filename in os.listdir(ocr_folder_path):
            if filename.startswith(basename) and filename.endswith('.txt'):
                page_files.append(filename)

        page_files = sorted(page_files, key=lambda x: int(x.split('.pdf_page_')[1].split('.txt')[0]))

        for page_file in page_files:
            ocr_file_path = os.path.join(ocr_folder_path, page_file)
            with open(ocr_file_path, "r", encoding="utf-8") as ocr_file:
                content = ocr_file.read()
                all_text += content + "\n\n"

        formatted_entry = {
            "category": category,
            "qid": basename,
            "content": all_text.strip()
        }
        formatted_data.append(formatted_entry)
        print(formatted_entry)

    return formatted_data


if __name__ == "__main__":
    """
    Main entry point of the script. Processes FAQ, finance, and insurance OCR data,
    consolidates them, and saves the result to a JSON file.
    """
    total_formatted_data = []

    # handle faq
    faq_data = check_text(FAQ_FILEPATH, "faq")
    total_formatted_data.extend(faq_data)

    # read finance ocr
    finance_data = read_ocr_files(FINANCE_OCR_FOLDER_PATH, "finance")
    total_formatted_data.extend(finance_data)

    # read insurance ocr
    insurance_data = read_ocr_files(INSURANCE_OCR_FOLDER_PATH, "insurance")
    total_formatted_data.extend(insurance_data)

    # store the data after cleaning in formatted_reference_ocr.json
    output_json_path = "data/formatted_reference_ocr.json"
    # os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as formatted_file:
        json.dump(total_formatted_data, formatted_file, ensure_ascii=False, indent=4)

    print("The process is finished and the result is saved in dataset/formatted_reference_ocr.json")
