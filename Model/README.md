# 執行檢索的主程式

## 使用技術
- Hybrid Search (Stage 1 --> Get Top 100)
    - OpenAI Embedding Model (Semantic search): `text-embedding-3-large` (50% Search)
    - Bm25 (Keyword search): `weaviate gse (jieba)` (50% Search)
- Voyage Reranker (Stage 2 --> Get Top 1)

## flask_app.py
- `/` 是 API Docs, `/api/chat/` 是我們的 Retrieval API

會開出一個 API 供 main.py 呼叫，每次呼叫會送入一題問題，並回傳一個答案 pid

## utils/retrieval_agent.py
負責呼叫 weaviate & voyage reranker 進行檢索

## utils/config_log.py
負責處理 config 檔案，並設定 log 檔案
