import os
import weaviate
from langchain.embeddings import OpenAIEmbeddings
import utils.config_log as config_log
import voyageai

# 載入設定檔案和日誌設定
config, logger, CONFIG_PATH = config_log.setup_config_and_logging()
config.read(CONFIG_PATH)

# 從 config 中取得 Weaviate URL 和 API 金鑰
wea_url = config.get('Weaviate', 'weaviate_url')
voyage_api_key = config.get('VoyageAI', 'api_key')
PROPERTIES = ['pid', 'content']

# 設定 OpenAI API 金鑰
os.environ['OPENAI_API_KEY'] = config.get('OpenAI', 'api_key')

class WeaviateSemanticSearch:
    def __init__(self, classnm):
        self.url = wea_url
        self.embeddings = OpenAIEmbeddings(chunk_size=1, model='text-embedding-3-large')
        self.client = weaviate.Client(url=wea_url)
        self.classnm = classnm

    def hybrid_search(self, query, source, num, alpha):
        query_vector = self.embeddings.embed_query(query)
        vector_str = ','.join(map(str, query_vector))

        where_conditions = ' '.join([
            f'{{path: ["pid"], operator: Equal, valueText: "{pid}"}}' for pid in source
        ])

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
    vo = voyageai.Client(api_key=api_key)
    reranking = vo.rerank(query, documents, model="rerank-2", top_k=1)
    top_result = reranking.results[0]

    # 根據內容找到相對應的 pid
    top_pid = pids[documents.index(top_result.document)]
    return {'pid': top_pid, 'relevance_score': top_result.relevance_score}


def search_do(question, category, source, alpha):
    if category == "finance":
        vdb_named = "Financedev"
    elif category == "insurance":
        vdb_named = "Insurancedev"
    else:
        vdb_named = "Faqdev"

    searcher = WeaviateSemanticSearch(vdb_named)
    # 從 Weaviate 取得前 100 筆結果
    top_100_results = searcher.hybrid_search(question, source, 100, alpha=alpha)
    
    # 準備文件和 pid 列表供 rerank 使用
    documents = [result['content'] for result in top_100_results]
    pids = [result['pid'] for result in top_100_results]

    # 使用 VoyageAI 重新排序，並取得排名最高的 pid
    top_reranked_result = rerank_with_voyage(question, documents, pids, voyage_api_key)

    print("最相關文件的 PID:")
    print(f"PID: {top_reranked_result['pid']}")
    print(f"相關性分數: {top_reranked_result['relevance_score']}")
    
    return top_reranked_result['pid']
