from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required
from service.database import create_user, get_user, verify_password
from service.elastic import Elastic
from models import db, User

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    if get_user(username):
        return jsonify({'error': 'Username already exists'}), 409
    create_user(username, password)
    return jsonify({'message': 'Registration successful'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    user = get_user(username)
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401
    login_user(user)
    return jsonify({'message': 'Login successful'}), 200

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200

elastic = Elastic()

@app.route('/searchPatents', methods=['GET'])
@login_required
def search_patents():
    query_params = request.args.to_dict(flat=True)
    query_params['page'] = int(query_params.get('page', 1))
    query_params['size'] = int(query_params.get('size', 10))

    filters = parse_filters(query_params.pop('filter', ''))
    query = query_params.get('query', '')
    for key, value in filters.items():
        if key == 'title':
            query = f"({query} AND title:{value})" if query else f"title:{value}"
        elif key == 'author':
            query_params['authors'] = f"{query_params.get('authors','')},{value}".strip(',')
        elif key == 'organization':
            query_params['organizations'] = f"{query_params.get('organizations','')},{value}".strip(',')
        elif key == 'publication_date':
            start_date, end_date = value.split('-')
            query_params['publication_start_date'] = start_date
            query_params['publication_end_date'] = end_date
        elif key == 'application_date':
            start_date, end_date = value.split('-')
            query_params['application_start_date'] = start_date
            query_params['application_end_date'] = end_date
        elif key == 'topic':
            query_params['topics'] = f"{query_params.get('topics','')},{value}".strip(',')

    query_params['query'] = query
    result = elastic.search_patents(**query_params)
    return jsonify({'total': result['hits']['total']['value'], 'items': result['hits']['hits']})

@app.route('/getPatentById', methods=['GET'])
@login_required
def get_patent_by_id():
    patent_id = request.args.get('_id')
    if not patent_id:
        return jsonify({'error': 'Missing patent ID'}), 400
    result = elastic.search_by_id(patent_id)
    return jsonify(result)

@app.route('/countPatentsInfos', methods=['GET'])
@login_required
def count_patents_infos():
    query_params = request.args.to_dict(flat=True)
    result = elastic.count_patents_infos(**query_params)
    return jsonify({'count': result})

if __name__ == '__main__':
    app.run(debug=True)
