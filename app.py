from flask import Flask, request, jsonify, make_response
from index import visualize_regex_railroad
from flask_cors import CORS
from check import validate_regex

app = Flask(__name__)
CORS(app)  # 允许所有来源的跨域请求

@app.route('/generate-diagram', methods=['POST', 'OPTIONS'])
def generate_diagram():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    data = request.get_json()
    regex_pattern = data.get('regexPattern', '')
    flag = validate_regex(regex_pattern)

    if not regex_pattern:
        return jsonify({'error': 'No regex pattern provided'}), 400

    if flag:
        visualize_regex_railroad(regex_pattern)

    return jsonify({'message': 'SVG file has been generated!'})

if __name__ == '__main__':
    app.run(debug=True, port=8001)