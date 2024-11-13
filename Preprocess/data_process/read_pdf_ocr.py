import os
import zipfile

import pytesseract
from pdf2image import convert_from_bytes

# Configure Tesseract path if necessary
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def ocr_cond_in_floder(zip_path, folder):
    folder_path = f'{folder}/'
    file_ratios = []

    with zipfile.ZipFile(zip_path, 'r') as zipf:
        # Select the files that the content can only be captued with OCR
        # by finding its compression ratio and original size
        for zip_info in zipf.infolist():
            if zip_info.filename.startswith(folder_path) and not zip_info.is_dir():
                original_size = zip_info.file_size  # Uncompressed size
                compressed_size = zip_info.compress_size  # Compressed size

                # Avoid division by zero for empty files
                if compressed_size > 0:
                    compression_ratio = 1 - (compressed_size / original_size)
                else:
                    compression_ratio = float('inf')  # Assign infinite ratio for empty files

                # Since we decide to OCR all the files, the code below is marked down
                # if (compression_ratio >= 0.1)
                # or (compression_ratio >= 0.05
                # and (original_size > 750*1024 or original_size < 170*1024))
                # or (original_size > 1500*1024) or (original_size < 120*1024):
                file_ratios.append((zip_info.filename, compression_ratio))

        # Sort by compression ratio in descending order
        file_ratios.sort(key=lambda x: x[1], reverse=False)

        for file_name, _ in file_ratios:
            with zipf.open(file_name) as pdf_file:
                pdf_bytes = pdf_file.read()

                # Specify the path to the Poppler binaries if needed
                poppler_path = r'C:\Program Files\poppler-24.08.0\Library\bin'

                # Convert the PDF bytes to images
                images = convert_from_bytes(pdf_bytes, dpi=300, poppler_path=poppler_path)

                # Create output directory
                output_dir = 'output_text'
                os.makedirs(output_dir, exist_ok=True)

                # Perform OCR on each page and save the text
                for i, image in enumerate(images):
                    text = pytesseract.image_to_string(image, lang='chi_tra')  # Specify the language for OCR
                    # Create subdirectory structure within 'output_text'
                    output_file_path = os.path.join(output_dir, f'{file_name}_page_{i + 1}.txt')
                    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
                    with open(os.path.join(output_dir, f'{file_name}_page_{i + 1}.txt'), 'w', encoding='utf-8') as f:
                        f.write(text)
                print(f'OCR completed for {file_name}')

    # return file_ratios


# Usage
zip_path = 'datazip.zip'
ocr_cond_in_floder(zip_path, '競賽資料集/reference/finance')
ocr_cond_in_floder(zip_path, '競賽資料集/reference/insurance')
