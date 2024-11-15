# AI CUP 2024 玉山人工智慧公開挑戰賽－RAG與LLM在金融問答的應用

## 使用技術

### Retriever

- Hybrid Search (Stage 1 --> Get Top 100)
    - OpenAI Embedding Model (Semantic search): `text-embedding-3-large` (50% Search)
    - Bm25 (Keyword search): `weaviate gse (jieba)` (50% Search)
- Voyage Reranker (Stage 2 --> Get Top 1)

### Data Preprocess

- 使用 Tesseract OCR & PDF Plumber/Miner 將 PDF 轉換為文字
- 利用 text_splitter 來 chunk tokens 數過多的資料
   - 2000 tokens 一切、500 tokens 重疊

## Repo Structure
```
.
├── .github
│   ├── contribute_guide.md
│   └── workflows
│       └── ci.yml
├── .gitignore # 讓 git 忽略的檔案和目錄 (e.g. cache, logs, etc.)
├── .pre-commit-config.yaml # 設定 pre-commit hooks 以檢查與格式化代碼、環境配置、Git 設定及檢測敏感資訊
├── .ruff.toml # ruff 設定檔，lint: pep8-naming, pycodestyle, pyflakes, etc.
├── LICENSE # MIT License
├── Model
│   ├── README.md
│   ├── flask_app.py
│   └── utils
│       ├── README.md
│       ├── __init__.py
│       ├── config_log.py
│       └── retrieval_agent.py
├── Preprocess
│   ├── README.md
│   ├── data_process
│   │   ├── README.md
│   │   ├── conbine_readpdf_result.py
│   │   ├── merge_with_ocr_pdfminer.py
│   │   ├── read_pdf_noocr.py
│   │   └── read_pdf_ocr.py
│   └── insert_data.py
├── README.md
├── config_example.ini # 設定檔範例，需自己複製一份成 config.ini 並修改
├── data
│   └── README.md
├── docker
│   ├── README.md
│   ├── docker-compose.yml
│   └── docker_install.sh
├── main.py # 主程式
├── requirements.txt # Python pip 環境需求
└── testing
    ├── README.md
    ├── checkans.py
    └── get_best_alpha.py
```

## Setup Environment
- **OS:** 除了 Data processing 使用 Windows, 其他以 MacOS, Linux 為主, Windows 需安裝 WSL2 等來模擬出 Linux 環境

To set up the development environment, follow these steps:

1. Create a virtual environment:
   ```
   python3 -m venv aicup_venv
   source aicup_venv/bin/activate
   ```

2. git clone our repo:
   ```
   git clone https://github.com/JustinHsu1019/AICUP2024-RAG-LLM.git
   cd AICUP2024-RAG-LLM
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Copy the configuration example and create your own config file:
   ```
   cp config_example.ini config.ini
   ```

5. Manually add your `secret key` to the `config.ini`:

- [OpenAI] 的 api_key 可以在 openai 官網註冊取得
- [VoyageAI] 的 api_key 可以在 voyageai 官網註冊取得
- [Api_docs] 的 password 可以自己隨意輸入
    - flask_app.py 啟動後，直接訪問 http://127.0.0.1:5000/ 即可看到 Swagger API 文件頁面

6. Create a `logs` directory:
   ```
   mkdir logs
   ```

7. Navigate to the `docker` directory:
   ```
   cd docker
   ```

8. Start the Docker environment (weaviate database):
- 首先將 docker-compose.yml 的 `OPENAI_APIKEY: ${OPENAI_APIKEY}` 改成你的 API Key
- 接著啟動 Docker Compose
   ```
   docker-compose up -d
   ```

9. Data preprocessing (這一階段因不同組員處理原因，OS 環境為 Windows):
- **Tesseract-OCR**：
  - 下載並安裝 Tesseract-OCR。
  - 安裝完成後，記下安裝路徑（如 `C:\Program Files\Tesseract-OCR\tesseract.exe`）。

- **Poppler**：
   - 下載並安裝 Poppler。
   - 安裝完成後，記下 `poppler_path`（如 `C:\Program Files\poppler-24.08.0\Library\bin`）。

在程式碼中配置 Tesseract 和 Poppler 的路徑：

    ```python
    # Configure Tesseract path if necessary (update this path as needed)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    # Specify the path to the Poppler binaries
    poppler_path = r"C:\Program Files\poppler-24.08.0\Library\bin"
    ```

確保將上述路徑替換為本地實際安裝的路徑。

確保您的 ZIP 文件包含以下資料夾和文件 (下載官方 dataset 後)：

    - `競賽資料集/reference/faq/pid_map_content.json`
    - `競賽資料集/reference/finance/*.pdf`
    - `競賽資料集/reference/insurance/*.pdf`

運行 data preprocess scripts:

   ```
   python3 Proprocess/data_process/data_preprocess.py
   python3 Preprocess/data_process/read_pdf_noocr.py
   python3 Preprocess/data_process/conbine_readpdf_result.py
   ```

10. Data insert to weaviate:
   ```
   python3 Preprocess/insert_data.py
   ```

11. Run the Flask app (`/` 是 API Docs, `/api/chat/` 是我們的 Retrieval API):
   ```
   python3 Model/flask_app.py
   ```

12. 將主辦方提供的題目 json 檔案改名為 questions.json 並塞入 data/

13. 運行 main.py 進行測試得出 data/pred_retrieve.json 提交最終結果給主辦方:
   ```
   python3 main.py
   ```

## Folder-specific Details
For more detailed information about each folder and its purpose, refer to the individual `README.md` files located in their respective directories.
