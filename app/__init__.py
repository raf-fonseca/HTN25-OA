from flask import Flask, jsonify, request
from app.database.models import get_all_users, get_user_by_email, update_user

def create_app():
    app = Flask(__name__)
    
    @app.route('/')
    def hello_world():
        return 'Hello, World!'
    
    @app.route('/users', methods=['GET'])
    def get_users():
        users = get_all_users()
        return jsonify([user.to_dict() for user in users])
    
    @app.route('/users/<email>', methods=['GET'])
    def get_user(email):
        user = get_user_by_email(email)
        if user is None:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user.to_dict())
    
    @app.route('/users/<email>', methods=['PUT'])
    def update_user_route(email):
        data = request.get_json()
        try:
            updated_user = update_user(email, data)
            return jsonify(updated_user.to_dict())
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
    
    return app 