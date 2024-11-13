import json
import os

from pdfminer.high_level import extract_text

# 文件路径
FAQ_FILEPATH = 'reference/faq/pid_map_content.json'
FINANCE_FOLDER_PATH = 'reference/finance'
INSURANCE_FOLDER_PATH = 'reference/insurance'
OCR_FOLDER_PATH = 'dataset/output_text/競賽資料集/reference'


def check_text(file_path, category):
    """处理 FAQ 文件，返回格式化的数据列表。"""
    formatted_data = []
    with open(file_path, encoding='utf-8') as faq_file:
        loaded_faq = json.load(faq_file)

    for qid, questions in loaded_faq.items():
        for question_item in questions:
            formatted_entry = {
                'category': category,
                'qid': qid,
                'content': {'question': question_item['question'], 'answers': question_item['answers']},
            }
            formatted_data.append(formatted_entry)
            print(formatted_entry)
    return formatted_data


def check_pdf_with_table(folder_path, category):
    """处理 PDF 文件，返回格式化的数据列表和需要 OCR 的文件列表。"""
    formatted_data = []
    need_to_ocr = []

    file_list = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    sorted_file_list = sorted(file_list, key=lambda x: int(os.path.splitext(x)[0]))

    for filename in sorted_file_list:
        filename_without_ext, _ = os.path.splitext(filename)
        file_path = os.path.join(folder_path, filename)
        all_text = ''

        try:
            # 获取 PDF 的总页数
            from pdfminer.pdfpage import PDFPage

            with open(file_path, 'rb') as f:
                total_pages = len(list(PDFPage.get_pages(f)))
        except Exception as e:
            print(f'无法获取文件 {file_path} 的页数：{e}')
            need_to_ocr.append([category, filename, 'all pages'])
            continue

        for page_number in range(total_pages):
            ocr_file_path = os.path.join(
                OCR_FOLDER_PATH, category, f'{filename_without_ext}.pdf_page_{page_number + 1}.txt'
            )

            try:
                # 尝试读取 OCR 生成的文本文件
                with open(ocr_file_path, encoding='utf-8') as ocr_file:
                    content = ocr_file.read()
            except FileNotFoundError:
                # 如果没有 OCR 文件，则从 PDF 中提取该页的文本
                try:
                    content = extract_text(file_path, page_numbers=[page_number]) or ''
                except Exception as e:
                    print(f'提取文件 {file_path} 第 {page_number + 1} 页时出错：{e}')
                    content = ''

            if content:
                # signal_character_lines = sum(
                #     1 for line in content.split("\n") if len(line.strip()) == 1
                # )
                all_text += content + '\n\n'

                # if signal_character_lines >= 40:
                #     need_to_ocr.append([category, filename, f"page{page_number + 1}"])
            else:
                need_to_ocr.append([category, filename, f'page{page_number + 1}'])

        formatted_entry = {'category': category, 'qid': filename_without_ext, 'content': all_text.strip()}
        formatted_data.append(formatted_entry)
        print(formatted_entry)

    return formatted_data, need_to_ocr


if __name__ == '__main__':
    # 总的格式化数据列表和需要 OCR 的文件列表
    total_formatted_data = []
    total_need_to_ocr = []

    # 处理 FAQ 文件
    faq_data = check_text(FAQ_FILEPATH, 'faq')
    total_formatted_data.extend(faq_data)

    # 处理金融类 PDF 文件
    finance_data, finance_need_to_ocr = check_pdf_with_table(FINANCE_FOLDER_PATH, 'finance')
    total_formatted_data.extend(finance_data)
    total_need_to_ocr.extend(finance_need_to_ocr)

    # 处理保险类 PDF 文件
    insurance_data, insurance_need_to_ocr = check_pdf_with_table(INSURANCE_FOLDER_PATH, 'insurance')
    total_formatted_data.extend(insurance_data)
    total_need_to_ocr.extend(insurance_need_to_ocr)

    # 将整理好的数据存入 formatted_reference_ocr.json
    with open('dataset/formatted_reference_ocr_pdfminer.json', 'w', encoding='utf-8') as formatted_file:
        json.dump(total_formatted_data, formatted_file, ensure_ascii=False, indent=4)

    # 将需要 OCR 的文件列表存入 need_to_ocr.txt
    with open('dataset/need_to_ocr_again_pdfminer.txt', 'w', encoding='utf-8') as ocr_file:
        json.dump(total_need_to_ocr, ocr_file, ensure_ascii=False, indent=4)

    print(f'需要 OCR 的文件数量: {len(total_need_to_ocr)}')
