from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__, static_folder='static')
CORS(app)

BASE = 'https://laresgroup.amocrm.ru'

@app.route('/')
def index():
    return send_from_directory('static', 'delete.html')

@app.route('/api/contacts/<path:path>')
def proxy_contacts(path):
    token = request.headers.get('X-Token')
    if not token:
        return jsonify({'error': 'No token'}), 401
    params = dict(request.args)
    try:
        r = requests.get(
            f'{BASE}/api/v4/{path}',
            headers={'Authorization': f'Bearer {token}'},
            params=params,
            timeout=15
        )
        return (r.content, r.status_code, {'Content-Type': 'application/json'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    token = request.headers.get('X-Token')
    if not token:
        return jsonify({'error': 'No token'}), 401
    try:
        r = requests.delete(
            f'{BASE}/api/v4/contacts/{contact_id}',
            headers={'Authorization': f'Bearer {token}'},
            timeout=15
        )
        return ('', r.status_code)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5056))
    app.run(host='0.0.0.0', port=port)
