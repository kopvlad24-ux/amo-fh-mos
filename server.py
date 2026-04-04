from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__, static_folder='static')
CORS(app)

def get_base(req):
    domain = req.headers.get('X-Domain', '').strip().rstrip('/')
    if not domain:
        return None, ('No X-Domain header', 400)
    if not domain.startswith('http'):
        domain = 'https://' + domain
    return domain, None

@app.route('/')
def index():
    return send_from_directory('static', 'delete.html')

@app.route('/api/contacts')
def get_contacts():
    token = request.headers.get('X-Token')
    if not token:
        return jsonify({'error': 'No token'}), 401

    base, err = get_base(request)
    if err:
        return jsonify({'error': err[0]}), err[1]

    params = dict(request.args)
    try:
        r = requests.get(
            f'{base}/api/v4/contacts',
            headers={'Authorization': f'Bearer {token}'},
            params=params,
            timeout=15
        )
        return (r.content, r.status_code, {'Content-Type': 'application/json'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete', methods=['DELETE'])
def delete_contacts():
    """
    Принимает JSON: [{"id": 123}, {"id": 456}, ...]
    Шлёт в AMO DELETE /api/v4/contacts с тем же телом (батч до 40 штук).
    """
    token = request.headers.get('X-Token')
    if not token:
        return jsonify({'error': 'No token'}), 401

    base, err = get_base(request)
    if err:
        return jsonify({'error': err[0]}), err[1]

    body = request.get_json(silent=True)
    if not body or not isinstance(body, list):
        return jsonify({'error': 'Body must be a JSON array of {id} objects'}), 400

    try:
        r = requests.delete(
            f'{base}/api/v4/contacts',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            json=body,
            timeout=20
        )
        # AMO возвращает 202 при успехе батч-удаления
        return (r.content or b'', r.status_code, {'Content-Type': 'application/json'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5056))
    app.run(host='0.0.0.0', port=port)
