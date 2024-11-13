# AI CUP 2024 玉山人工智慧公開挑戰賽－RAG與LLM在金融問答的應用

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
To set up the development environment, follow these steps:

1. Create a virtual environment:
   ```
   python3 -m venv aicup_venv
   source aicup_venv/bin/activate
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Copy the configuration example and create your own config file:
   ```
   cp config_example.ini config.ini
   ```

4. Manually add your `secret key` to the `config.ini`.
   (需展開解釋 config.ini 內的每一項 key)

5. Create a `logs` directory:
   ```
   mkdir logs
   ```

6. Navigate to the `docker` directory:
   ```
   cd docker
   ```

7. Start the Docker environment (weaviate database):
   ```
   docker-compose up -d
   ```

8. Data preprocessing:

9. Data insert to weaviate:

10. Run the Flask app:
   ```
   python3 src/flask_app.py
   ```

11. 將主辦方提供的 questions.json 測試資料塞入 data/:

12. 運行 main.py 進行測試得出 data/pred_retrieve.json 提交最終結果給主辦方:


## Folder-specific Details
For more detailed information about each folder and its purpose, refer to the individual `README.md` files located in their respective directories.
