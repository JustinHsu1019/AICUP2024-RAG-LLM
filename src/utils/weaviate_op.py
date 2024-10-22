import os

import weaviate
from langchain.embeddings import OpenAIEmbeddings

import utils.config_log as config_log

config, logger, CONFIG_PATH = config_log.setup_config_and_logging()
config.read(CONFIG_PATH)

wea_url = config.get('Weaviate', 'weaviate_url')
PROPERTIES = ['uuid', 'title', 'content']

os.environ['OPENAI_API_KEY'] = config.get('OpenAI', 'api_key')


# TODO: 添加 Reranker
class WeaviateSemanticSearch:
    def __init__(self, classnm):
        self.url = wea_url
        self.embeddings = OpenAIEmbeddings(chunk_size=1, model='text-embedding-3-large')
        self.client = weaviate.Client(url=wea_url)
        self.classnm = classnm

    def aggregate_count(self):
        return self.client.query.aggregate(self.classnm).with_meta_count().do()

    def get_all_data(self, limit=3):
        if self.client.schema.exists(self.classnm):
            result = self.client.query.get(class_name=self.classnm, properties=PROPERTIES).with_limit(limit).do()
            return result
        else:
            raise Exception(f'Class {self.classnm} does not exist.')

    def delete_class(self):
        self.client.schema.delete_class(self.classnm)

    # TODO: 完善 CKIP keyword Search (目前 score 皆為 0)
    def hybrid_search(self, query, num, alpha):
        query_vector = self.embeddings.embed_query(query)
        vector_str = ','.join(map(str, query_vector))
        gql_query = f"""
        {{
            Get {{
                {self.classnm}(hybrid: {{query: "{query}", vector: [{vector_str}], alpha: {alpha} }}, limit: {num}) {{
                    title
                    content
                    _additional {{
                        distance
                        score
                    }}
                }}
            }}
        }}
        """
        search_results = self.client.query.raw(gql_query)

        if 'errors' in search_results:
            raise Exception(search_results['errors'][0]['message'])

        results = search_results['data']['Get'][self.classnm]
        return results


def search_do(input_, alp):
    vdb_named = config.get('Weaviate', 'classnm')

    searcher = WeaviateSemanticSearch(vdb_named)
    results = searcher.hybrid_search(input_, 10, alpha=alp)

    result_li = []
    for _, result in enumerate(results, 1):
        result_li.append({'title': result['title'], 'content': result['content']})

    return result_li


if __name__ == '__main__':
    vdb = config.get('Weaviate', 'classnm')
    client = WeaviateSemanticSearch(vdb)

    # 統計筆數
    count_result = client.aggregate_count()
    print(count_result)

    # 輸出所有資料
    data_result = client.get_all_data()
    print(data_result)

    # 刪除此向量庫
    # client.delete_class()

    # An alpha of 1 is a pure vector search
    # An alpha of 0 is a pure keyword search
    # quest = "幫我找專任助理"
    # print(search_do(quest, alp=0.5))
