import weaviate
from langchain.embeddings import OpenAIEmbeddings
import sys
import os
import warnings
from contextlib import redirect_stdout, redirect_stderr

from utils.ckip import ws_driver, pos_driver, clean
import utils.config_log as config_log


config, logger, CONFIG_PATH = config_log.setup_config_and_logging()
config.read(CONFIG_PATH)

wea_url = config.get("Weaviate", "weaviate_url")
PROPERTIES = ["uuid", "content"]

os.environ["OPENAI_API_KEY"] = config.get("OpenAI", "api_key")

# 忽略所有的 DeprecationWarning
warnings.filterwarnings("ignore", category=DeprecationWarning)


def silent_call_ckip_v2(question):
    # 保存當前的 sys.stdout 和 sys.stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    try:
        # 使用 with 確保 stdout 和 stderr 正確地關閉，靜默所有輸出
        with open(os.devnull, "w") as fnull:
            with redirect_stdout(fnull), redirect_stderr(fnull):
                ws = ws_driver([question])
                pos = pos_driver(ws)
    finally:
        # 恢復 sys.stdout 和 sys.stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr
    return ws, pos


class WeaviateSemanticSearch:
    def __init__(self, classNm, keyclassNm):
        self.url = wea_url
        self.embeddings = OpenAIEmbeddings(chunk_size=1, model="text-embedding-3-large")
        self.client = weaviate.Client(url=wea_url)
        self.classNm = classNm
        self.keyclassNm = keyclassNm

    def vector_search(self, query_text, num_results=1000):
        query_vector = self.embeddings.embed_query(query_text)
        vector_str = ",".join(map(str, query_vector))

        # TODO: 加入 where 篩選出 sources
        gql_query = f"""
        {{
            Get {{
                {self.classNm}(hybrid: {{query: "{query_text}", vector: [{vector_str}], alpha: 1 }}, limit: {num_results}) {{
                    uuid
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
        results = search_results["data"]["Get"][self.classNm]
        return results

    def keyword_search(self, query_text, num_results=1000):
        # TODO: 加入 where 篩選出 sources
        gql_query = f"""
        {{
            Get {{
                {self.keyclassNm}(hybrid: {{query: "{query_text}", vector: [], alpha: 0 }}, limit: {num_results}) {{
                    uuid
                    content
                    _additional {{
                        score
                    }}
                }}
            }}
        }}
        """
        search_results = self.client.query.raw(gql_query)
        results = search_results["data"]["Get"][self.keyclassNm]
        return results

    def hybrid_search(self, vector_results, keyword_results, alpha, num_results=1):
        vector_scores = {
            result["uuid"]: float(result["_additional"]["score"])
            for result in vector_results
        }
        keyword_scores = {
            result["uuid"]: float(result["_additional"]["score"])
            for result in keyword_results
        }

        all_ids = set(vector_scores.keys()).union(keyword_scores.keys())
        combined_scores = {}

        for doc_id in all_ids:
            vec_score = vector_scores.get(doc_id, 0)
            key_score = keyword_scores.get(doc_id, 0)

            """ test: score log """
            # print("vec: " + str(vec_score))
            # print("key: " + str(key_score))

            combined_score = alpha * vec_score + (1 - alpha) * key_score
            combined_scores[doc_id] = combined_score

        sorted_combined_scores = sorted(
            combined_scores.items(), key=lambda x: x[1], reverse=True
        )
        top_ids = [item[0] for item in sorted_combined_scores[:num_results]]

        return top_ids


def for_aicup(question, category, source):
    # classnm: faq, faq_key, finance, finance_key, insurance, insurance_key
    ####
    if category == "":
        searcher = WeaviateSemanticSearch(
            config.get("Weaviate", ""), config.get("Weaviate", "")
        )
    elif category == "":
        searcher = WeaviateSemanticSearch(
            config.get("Weaviate", ""), config.get("Weaviate", "")
        )
    ####

    ws = ws_driver([question])
    pos = pos_driver(ws)
    ws, pos = silent_call_ckip_v2(question)
    keyword = clean(ws[0], pos[0])

    vector_results = searcher.vector_search(question, len(source))
    keyword_results_search = searcher.keyword_search(keyword, len(source))
    alpha = 0.5

    result = searcher.hybrid_search(
        vector_results, keyword_results_search, alpha, num_results=1
    )

    return result # response uuid, title and content JSON
