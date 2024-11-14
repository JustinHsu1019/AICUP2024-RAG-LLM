# 資料前處理使用指南
此資料夾為資料預處理的程式碼
- OCR & PDF 文字直接讀取

## 簡介

此程式碼包含用於讀取與處理 Reference 檔案夾中 FAQ（JSON）文件和 Finance 與 Insurance（PDF）文本文件的 Python 程式碼。程式碼的主要功能包括：

- 先從 ZIP 壓縮檔案中提取指定資料夾內的 PDF 文件，再將每一頁轉換為圖像，並使用 Tesseract 進行 OCR 識別以提取文本內容。將提取的文本內容保存為 `.txt` 文件，按類別分類儲存。
- 再讀取 FAQ JSON 文件和 OCR 生成的文本文件，將所有資料格式化並合併為一個統一的 JSON 文件，便於後續的檢索與處理。

## 運行環境和套件

### Python 套件

- `pytesseract`
- `pdf2image`
- `zipfile`（標準函式庫）
- `json`（標準函式庫）
- `os`（標準函式庫）

### 外部套件

- **Tesseract-OCR**：用於 OCR 識別。
  - 下載地址：[Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
  - 安裝路徑示例：`C:\Program Files\Tesseract-OCR\tesseract.exe`
- **Poppler**：用於 PDF 轉圖片。
  - 下載地址：[Poppler for Windows](http://blog.alivate.com.au/poppler-windows/)
  - 安裝路徑示例：`C:\Program Files\poppler-24.08.0\Library\bin`

## 安裝

### 1. 複製或下載專案

如果您尚未獲取專案代碼，請複製或下載到本地：

```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```


### 2. 安裝外部套件

- **Tesseract-OCR**：
  - 下載並安裝 Tesseract-OCR。
  - 安裝完成後，記下安裝路徑（如 `C:\Program Files\Tesseract-OCR\tesseract.exe`）。

- **Poppler**：
  - 下載並安裝 Poppler。
  - 安裝完成後，記下 `poppler_path`（如 `C:\Program Files\poppler-24.08.0\Library\bin`）。

### 3. 安裝 Python 套件

安裝所需的 Python 套件：

```bash
pip install pytesseract==0.3.13
pip install pdf2image==1.17.0
```

## 配置

在程式碼中配置 Tesseract 和 Poppler 的路徑：

```python
# Configure Tesseract path if necessary (update this path as needed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Specify the path to the Poppler binaries
poppler_path = r"C:\Program Files\poppler-24.08.0\Library\bin"
```

確保將上述路徑替換為本地實際安裝的路徑。

## 使用說明

### 1. 準備資料

確保您的 ZIP 文件包含以下資料夾和文件：

- `競賽資料集/reference/faq/pid_map_content.json`
- `競賽資料集/reference/finance/*.pdf`
- `競賽資料集/reference/insurance/*.pdf`

### 2. 運行 OCR 提取

運行以下命令進行 OCR 處理：

```bash
python data_preprocess.py
```

程式碼將執行以下步驟：

1. 從指定的 ZIP 文件中提取 Finance 和 Insurance 的 PDF 文件。
2. 將每個 PDF 文件的每一頁轉換為圖像。
3. 使用 Tesseract 進行 OCR 識別，提取文本內容。
4. 將提取的文本保存為 `.txt` 文件，按類別儲存在 `dataset/output_text/finance/` 和 `dataset/output_text/insurance/` 目錄下。

### 3. 資料格式化

程式碼會繼續執行以下步驟：

1. 讀取 FAQ 文件 `pid_map_content.json`，提取問題和答案。
2. 讀取 OCR 生成的文本文件，按 PDF 文件和頁碼順序合併文本內容。
3. 將所有資料格式化並合併為一個 JSON 文件 `dataset/formatted_reference_ocr.json`。

### 4. 查看輸出

- **OCR 輸出文本文件**：
  - Finance 文本文件保存在 `dataset/output_text/finance/`。
  - Insurance 文本文件保存在 `dataset/output_text/insurance/`。

- **合併後的 JSON 文件**：
  - `dataset/formatted_reference_ocr.json` 包含了所有格式化後的 FAQ、Finance 與 Insurance 資料。

## 文件結構

```
project/
├── dataset/
│   ├── output_text/
│   │   └── 競賽資料集/
│   │       └── reference/
│   │           ├── finance/
│   │           │   ├── 0.pdf_page_1.txt
│   │           │   ├── 1.pdf_page_1.txt
│   │           │   ├── 1.pdf_page_2.txt
│   │           │   └── ...
│   │           └── insurance/
│   │               ├── 1.pdf_page_1.txt
│   │               ├── 1.pdf_page_2.txt
│   │               └── ...
│   └── formatted_reference_ocr.json
├── datazip.zip/
│   └── 競賽資料集/
│           └── reference/
│               ├── faq/
│               │   └── pid_map_content.json
│               ├── finance/
│               │   ├── 0.pdf
│               │   ├── 1.pdf
│               │   └── ...
│               └── insurance/
│                   ├── 1.pdf
│                   ├── 2.pdf
│                   └── ...
├── data_preprocess.py
└── README.md
```

## 範例輸出

生成的 `formatted_reference_ocr.json` 文件結構示例：

```json
[
    {
        "category": "faq",
        "qid": "0",
        "content": {
            "question": "什麼是跨境手機掃碼支付?",
            "answers": [
                "允許大陸消費者可以用手機支付寶App在台灣實體商店購買商品或服務"
            ]
        }
    },// 其他 FAQ 資料條目...
    {
        "category": "finance",
        "qid": "0",
        "content": "註 1U ﹕ 本 雄 團 於 民 國 111] 年 第 1 季 投 賁 成 立 寶 元 智 造 公 司 ， 由 本 集 圖 持\n有 100% 股 權 ， 另 於 民 國 111 年 第 3 季 及 112 年 第 1 季 未 依 持 股 比..."
    },// 其他 Finance 資料條目...
    {
        "category": "insurance",
        "qid": "1",
        "content": "延 期 間 內 發 生 第 十 六 條 或 第 十 七 條 本 公 司 應 負 係 險 貫 任 之 事 故 時 ， 其 約 定 之 係 險 金 計 算 方 式 將 不 適 用 ， 本 公\n..."
    },// 其他 Insurance 資料條目...
]
```

## 注意事項

- **編碼**：確保所有文本文件均使用 UTF-8 編碼，以支持中文字符，避免出現亂碼。
- **路徑配置**：
  - 請根據您本地的安裝路徑，更新程式碼中的 `tesseract_cmd` 和 `poppler_path` 變數。
- **文件命名**：
  - OCR 文本文件必須遵循 `{文件名}.pdf_page_{頁碼}.txt` 的命名規則，以確保程式碼能夠正確讀取並合併各頁內容。
- **套件安裝**：
  - 確保已正確安裝並配置 Tesseract-OCR 和 Poppler，否則程式碼將無法正常運行。

## 許可證

本專案採用 [MIT 許可證](LICENSE)。您可以自由地使用、修改和分發本專案。

---

**感謝您的使用！**
