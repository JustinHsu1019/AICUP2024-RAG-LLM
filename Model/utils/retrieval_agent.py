import os

import voyageai
import weaviate
from langchain.embeddings import OpenAIEmbeddings

import utils.config_log as config_log

config, logger, CONFIG_PATH = config_log.setup_config_and_logging()
config.read(CONFIG_PATH)

wea_url = config.get('Weaviate', 'weaviate_url')  # 此次所使用的向量資料庫
voyage_api_key = config.get('VoyageAI', 'api_key')  # Voyage Reranker 所使用的 API Key
PROPERTIES = ['pid', 'content']  # 向量資料庫中此 Class 的欄位

# 設定 OpenAI API 金鑰
os.environ['OPENAI_API_KEY'] = config.get('OpenAI', 'api_key')


class WeaviateSemanticSearch:
    """Weaviate 向量資料庫的搜尋類別"""

    def __init__(self, classnm):
        """初始化 Weaviate 向量資料庫的搜尋類別"""
        self.url = wea_url
        # 選擇的 OpenAI embedding model
        self.embeddings = OpenAIEmbeddings(chunk_size=1, model='text-embedding-3-large')
        self.client = weaviate.Client(url=wea_url)
        self.classnm = classnm

    def hybrid_search(self, query, source, num, alpha):
        """Weaviate 向量資料庫的搜尋方法"""
        query_vector = self.embeddings.embed_query(query)
        vector_str = ','.join(map(str, query_vector))

        # 下述兩搜索式主要為過濾出 source 中的 pid，並只針對 source 中的 pid 的文件進行 retrieval & rerank
        where_conditions = ' '.join([f'{{path: ["pid"], operator: Equal, valueText: "{pid}"}}' for pid in source])

        gql_query = f"""
        {{
            Get {{
                {self.classnm}(where: {{
                    operator: Or,
                    operands: [{where_conditions}]
                }}, hybrid: {{
                    query: "{query}",
                    vector: [{vector_str}],
                    alpha: {alpha}
                }}, limit: {num}) {{
                    pid
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


def rerank_with_voyage(query, documents, pids, api_key):
    """利用 Voyage Reranker 對 Weaviate hybrid search retrieval 的結果進行 rerank"""
    vo = voyageai.Client(api_key=api_key)
    # 利用 voyage rerank-2 從 hybrid search retrieval 中篩出的所有文件取出最終的 top 1
    reranking = vo.rerank(query, documents, model='rerank-2', top_k=1)
    top_result = reranking.results[0]

    top_pid = pids[documents.index(top_result.document)]
    return {'pid': top_pid, 'relevance_score': top_result.relevance_score}


def search_do(question, category, source, alpha):
    """flask_app.py 呼叫的 '搜尋' 主程式"""

    # 先根據題目給定的 category 選擇對應的向量資料庫 Class
    if category == 'finance':
        vdb_named = 'Financedev'
    elif category == 'insurance':
        vdb_named = 'Insurancedev'
    else:
        vdb_named = 'Faqdev'

    searcher = WeaviateSemanticSearch(vdb_named)
    # 從 Weaviate hybrid search retrieval 前 100 筆結果
    top_100_results = searcher.hybrid_search(question, source, 100, alpha=alpha)

    documents = [result['content'] for result in top_100_results]
    pids = [result['pid'] for result in top_100_results]

    # 使用 VoyageAI 重新排序，並取得排名最高的 pid
    top_reranked_result = rerank_with_voyage(question, documents, pids, voyage_api_key)

    # Log
    print('最相關文件的 PID:')
    print(f"PID: {top_reranked_result['pid']}")
    print(f"相關性分數: {top_reranked_result['relevance_score']}")

    return top_reranked_result['pid']
