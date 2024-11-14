# 此資料夾為所有處理資料的程式碼
包含 資料預處理 及 資料寫入資料庫

## data_process/
OCR & PDF 文字直接讀取

## insert_data.py
此程式為寫入資料庫的程式碼，並包含建立資料庫 class、對資料進行 embedding、利用 text_splitter 去 chunk tokens 數過多的資料
