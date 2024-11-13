import json
import time

import utils.config_log as config_log
import weaviate
from langchain.text_splitter import RecursiveCharacterTextSplitter

config, logger, CONFIG_PATH = config_log.setup_config_and_logging()
config.read(CONFIG_PATH)

wea_url = config.get('Weaviate', 'weaviate_url')
openai_api_key = config.get('OpenAI', 'api_key')

# Token limit for OpenAI model
TOKEN_LIMIT = 8192


class WeaviateManager:
    """Weaviate Insert data 管理器"""

    def __init__(self, classnm):
        """初始化 Weaviate 連接"""
        self.url = wea_url
        self.client = weaviate.Client(url=wea_url, additional_headers={'X-OpenAI-Api-Key': openai_api_key})
        self.classnm = classnm
        self.check_class_exist()

    def check_class_exist(self):
        """檢查 class 是否存在"""
        if self.client.schema.exists(self.classnm):
            print(f'{self.classnm} is ready')
            return True
        schema = {
            'class': self.classnm,
            'properties': [
                {'name': 'pid', 'dataType': ['text']},
                {
                    'name': 'content',
                    'dataType': ['text'],
                    'tokenization': 'gse',
                },  # `gse` implements the "Jieba" algorithm, which is a popular Chinese text segmentation algorithm.
            ],
            'vectorizer': 'text2vec-openai',
            'moduleConfig': {
                'text2vec-openai': {'model': 'text-embedding-3-large', 'dimensions': 3072, 'type': 'text'}
            },
        }
        print(f'creating {self.classnm}...')
        self.client.schema.create_class(schema)
        print(f'{self.classnm} is ready')
        return True

    def insert_data(self, pid, content):
        """插入資料到 Weaviate"""
        data_object = {'pid': pid, 'content': content}
        max_retries = 5
        for attempt in range(max_retries):
            try:
                self.client.data_object.create(data_object, self.classnm)
                return True  # 成功插入後結束方法
            except weaviate.exceptions.UnexpectedStatusCodeException as e:
                error_msg = str(e)
                # 檢查是否是因為 token 長度過長
                if 'maximum context length' in error_msg:
                    print(f'Content too long for pid: {pid}. Splitting content.')
                    return 'TOO_LONG'  # 特殊回傳值表達需要分割
                elif '429' in error_msg:
                    print(f'Rate limit exceeded, retrying in 5 seconds... (Attempt {attempt + 1}/{max_retries})')
                    time.sleep(5)
                else:
                    print(f'Unexpected Error for pid: {pid} - {error_msg}')
                    return False
            except Exception as e:
                print(f'Error inserting data for pid: {pid}, category: {self.classnm} - {str(e)}')
                return False
        # 超過最大重試次數
        print(f'Failed to insert data for pid: {pid} after {max_retries} attempts.')
        return False

    def split_and_insert(self, pid, content, category):
        """處理特例：分割並插入資料"""
        # 使用 TextSplitter 分割長文本
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=4096, chunk_overlap=500)
        split_content = text_splitter.split_text(content)

        # 逐段插入分割後的文本，保持相同的 pid 和 category
        for idx, part in enumerate(split_content):
            print(f'Inserting split content part {idx + 1} for pid: {pid}')
            success = self.insert_data(pid, part)
            if not success:
                failed_records.append({'pid': pid, 'category': category})


if __name__ == '__main__':
    with open('data/aicup_noocr_sec.json', encoding='utf-8') as file:
        data = json.load(file)

    failed_records = []  # 用於存放匯入失敗的資料

    for item in data:
        category = item['category']
        pid = item['pid']
        content = item['content']

        if category == 'faq':
            classnm = 'faqdev'
            content_str = json.dumps(content, ensure_ascii=False, indent=4)
        elif category == 'insurance':
            classnm = 'insurancedev'
            content_str = content
        elif category == 'finance':
            classnm = 'financedev'
            content_str = json.dumps(content, ensure_ascii=False, indent=4) if isinstance(content, dict) else content
        else:
            print('Unknown category, skipping item.')
            continue

        manager = WeaviateManager(classnm)
        result = manager.insert_data(pid, content_str)

        # 如果內容過長需要切割
        if result == 'TOO_LONG':
            manager.split_and_insert(pid, content_str, category)
        elif not result:  # 如果失敗且非長度問題
            failed_records.append({'pid': pid, 'category': category})

    # 將失敗的資料寫入 JSON 檔案
    if failed_records:
        with open('failed_imports.json', 'w', encoding='utf-8') as f:
            json.dump(failed_records, f, ensure_ascii=False, indent=4)
        print("Failed records have been written to 'failed_imports.json'")
    else:
        print('All records imported successfully.')
