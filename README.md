# AI CUP 2024 玉山人工智慧公開挑戰賽－RAG與LLM在金融問答的應用

## Repo Structure
```
(主要用 # 介紹沒有在 folder 內獨立檔案)
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
