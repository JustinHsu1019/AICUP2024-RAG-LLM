import utils.config_log as config_log
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_restx import Api, Resource, fields
from utils.retrieval_agent import search_do
from werkzeug.security import check_password_hash, generate_password_hash

config, logger, CONFIG_PATH = config_log.setup_config_and_logging()
config.read(CONFIG_PATH)

auth = HTTPBasicAuth()

users = {'aicup': generate_password_hash(config.get('Api_docs', 'password'))}


@auth.verify_password
def verify_password(username, password):
    """Verify password for API Docs"""
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None


app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type, Qs-PageCode, Cache-Control'

limiter = Limiter(get_remote_address, app=app)

api = Api(
    app,
    version='1.0',
    title='AICUP API',
    description='AICUP API',
)

ns = api.namespace('api', description='Chatbot operations')

model = api.model(
    'ChatRequest',
    {
        'qid': fields.Integer(required=True, description='qid of the question'),
        'source': fields.List(fields.Integer, required=True, description='source of the question'),
        'query': fields.String(required=True, description='The message to the chatbot'),
        'category': fields.String(required=True, description='The category of the question'),
    },
)


@ns.route('/')
class HealthCheck(Resource):
    """Server health check."""

    @api.doc('health_check')
    def get(self):
        """Server health check."""
        response = jsonify('server is ready')
        response.status_code = 200
        return response


@ns.route('/chat')
class ChatBot(Resource):
    """retrieve and rank api entry point"""

    @api.doc('chat_bot')
    @api.expect(model)
    def post(self):
        """retrieve and rank api entry point"""
        qid = request.json.get('qid')
        source = request.json.get('source')
        question = request.json.get('query')
        category = request.json.get('category')

        # for alpha testing (finding best hybrid search alpha)
        # alpha = request.json.get('alpha')

        # input template
        # {
        # "qid": 1,
        # "source": [442, 115, 440, 196, 431, 392, 14, 51],
        # "query": "匯款銀行及中間行所收取之相關費用由誰負擔?",
        # "category": "insurance"
        # },

        alpha = 0.5  # 最終因使用 Reranker 全盤處理 sources，故任何 alpha 對準確率都無影響

        if not question:
            # 為避免任何萬一，無論如何都須回傳一個結果，不做 Error logging
            response = jsonify({'qid': '1', 'retrieve': '1'})
            response.status_code = 200
            return response
        else:
            try:
                response = search_do(question, category, source, alpha)
                response = {'qid': qid, 'retrieve': int(response)}

                response = jsonify(response)

            except Exception:
                response = jsonify({'qid': qid, 'retrieve': source[-1]})
                response.status_code = 200
                return response

        try:
            response.status_code = 200
            return response
        except TypeError:
            # 為避免任何萬一，無論如何都須回傳一個結果，不做 Error logging
            response = jsonify({'qid': qid, 'retrieve': source[-1]})
            response.status_code = 200
            return response


# For API Docs
@app.before_request
def require_auth_for_docs():
    """Require authentication for API Docs"""
    if request.path == '/':
        return auth.login_required()(swagger_ui)()


# For API Docs
@app.route('/')
def swagger_ui():
    """Redirect to the Swagger UI"""
    return api.render_doc()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
