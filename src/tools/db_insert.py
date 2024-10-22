import time
import uuid

import utils.config_log as config_log
import weaviate

config, logger, CONFIG_PATH = config_log.setup_config_and_logging()
config.read(CONFIG_PATH)

wea_url = config.get('Weaviate', 'weaviate_url')
openai_api_key = config.get('OpenAI', 'api_key')


class WeaviateManager:
    def __init__(self, classnm):
        self.url = wea_url
        self.client = weaviate.Client(url=wea_url, additional_headers={'X-OpenAI-Api-Key': openai_api_key})
        self.classnm = classnm
        self.check_class_exist()

    def check_class_exist(self):
        if self.client.schema.exists(self.classnm):
            print(f'{self.classnm} is ready')
            return True
        schema = {
            'class': self.classnm,
            'properties': [
                {'name': 'uuid', 'dataType': ['text']},
                {'name': 'title', 'dataType': ['text']},
                {'name': 'content', 'dataType': ['text']},
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

    def insert_data(self, title_text, content_text):
        data_object = {'uuid': str(uuid.uuid4()), 'title': title_text, 'content': content_text}
        max_retries = 5
        for attempt in range(max_retries):
            try:
                self.client.data_object.create(data_object, self.classnm)
                break
            except weaviate.exceptions.RequestError as e:
                if '429' in str(e):
                    print(f'Rate limit exceeded, retrying in 5 seconds... (Attempt {attempt + 1}/{max_retries})')
                    time.sleep(5)
                else:
                    raise


# 資料倒入 template
if __name__ == '__main__':
    manager = WeaviateManager(config.get('Weaviate', 'classnm'))

    with open('data/xxx.txt', encoding='utf-8') as file:
        content = file.read()

    new_cp = content.split('aicup')

    for i in new_cp:
        lines = i.splitlines()
        if len(lines) > 1:
            first_line = lines[1]
            remaining_lines = '\n'.join(lines[2:])
            print('第一行' + first_line)
            print('剩下行' + remaining_lines)
            print('\n\n')
            manager.insert_data(first_line, remaining_lines)
