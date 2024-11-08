import utils.config_log as config_log
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_restx import Api, Resource, fields
from utils.weaviate_op import search_do
from werkzeug.security import check_password_hash, generate_password_hash

config, logger, CONFIG_PATH = config_log.setup_config_and_logging()
config.read(CONFIG_PATH)

auth = HTTPBasicAuth()

users = {'aicup': generate_password_hash(config.get('Api_docs', 'password'))}


@auth.verify_password
def verify_password(username, password):
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
        'category': fields.String(required=True, description='The category of the question')
    },
)


@ns.route('/')
class HealthCheck(Resource):
    @api.doc('health_check')
    def get(self):
        """Server health check."""
        response = jsonify('server is ready')
        response.status_code = 200
        return response


@ns.route('/chat')
class ChatBot(Resource):
    @api.doc('chat_bot')
    @api.expect(model)
    def post(self):
        qid = request.json.get('qid')
        source = request.json.get('source')
        question = request.json.get('query')
        category = request.json.get('category')

        # {
        # "qid": 1,
        # "source": [442, 115, 440, 196, 431, 392, 14, 51],
        # "query": "匯款銀行及中間行所收取之相關費用由誰負擔?",
        # "category": "insurance"
        # },

        if not question:
            response = jsonify({'qid': '1', 'retrieve': '1'})
            response.status_code = 200
            return response
        else:
            try:
                response = search_do(question, category, source)
                response = {
                    'qid': qid,
                    'retrieve': int(response)
                }

                response = jsonify(response)

            except Exception:
                response = jsonify({'qid': qid, 'retrieve': source[-1]})
                response.status_code = 200
                return response

        try:
            response.status_code = 200
            return response
        except TypeError:
            response = jsonify({'qid': qid, 'retrieve': source[-1]})
            response.status_code = 200
            return response


@app.before_request
def require_auth_for_docs():
    if request.path == '/':
        return auth.login_required()(swagger_ui)()


@app.route('/')
def swagger_ui():
    return api.render_doc()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
