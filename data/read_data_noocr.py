import json
import os

import pdfplumber
from tqdm import tqdm


# 讀取單個PDF文件並返回其文本內容
def read_pdf(pdf_loc):
    pdf = pdfplumber.open(pdf_loc)
    pdf_text = ''
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            pdf_text += text
    pdf.close()
    return pdf_text


# 從指定資料夾載入PDF文件，並根據資料夾名稱設定category
def load_data_by_category(source_path, category):
    pdf_files = [f for f in os.listdir(source_path) if f.endswith('.pdf')]
    data = []
    for file in tqdm(pdf_files):
        pid = file.replace('.pdf', '')  # 擷取檔案名稱作為pid
        content = read_pdf(os.path.join(source_path, file))  # 讀取PDF內文
        data.append({'category': category, 'pid': pid, 'content': content})
    return data


# 主程式
def generate_json(output_path):
    all_data = []

    # 載入不同類別的PDF資料
    source_paths = {
        'finance': 'reference/finance',  # finance 資料夾的路徑
        'insurance': 'reference/insurance',  # insurance 資料夾的路徑
    }

    # 遍歷每個類別的資料夾並載入資料
    for category, path in source_paths.items():
        category_data = load_data_by_category(path, category)
        all_data.extend(category_data)

    # 將結果儲存為 JSON 文件
    with open(output_path, 'w', encoding='utf8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)


# 設定輸出路徑
output_path = 'data/aicup_noocr.json'
generate_json(output_path)
