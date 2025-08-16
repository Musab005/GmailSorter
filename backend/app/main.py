# backend/app/main.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.app.core.rag_pipeline import RAGPipeline
import os

app = Flask(__name__)
CORS(app)

pipeline = None


def get_pipeline():
    global pipeline
    if pipeline is None:
        original_cwd = os.getcwd()
        core_dir = os.path.join(original_cwd, 'app', 'core') if 'backend' in original_cwd else os.path.join(
            original_cwd, 'backend', 'app', 'core')
        os.chdir(os.path.dirname(core_dir))  # Go to backend/app/
        pipeline = RAGPipeline()
        os.chdir(original_cwd)
    return pipeline


@app.route('/')
def index():
    return jsonify({"status": "API is running"})


@app.route('/api/query', methods=['POST'])
def query_endpoint():
    data = request.get_json()
    question = data.get('question')

    if not question:
        return jsonify({'error': 'No question provided.'}), 400

    rag_pipeline = get_pipeline()
    answer = rag_pipeline.query(question)

    return jsonify({'answer': answer})


if __name__ == '__main__':
    get_pipeline()
    app.run(host='0.0.0.0', port=5000)
