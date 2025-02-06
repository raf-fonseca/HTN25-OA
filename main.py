from flask import Flask, jsonify, request
from app.database.models import get_all_users, get_user_by_email, update_user, create_scan, get_scan_statistics
from app.database.schema import init_db
import sqlite3
from datetime import datetime

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

@app.route('/scan/<email>', methods=['PUT'])
def scan_route(email):
    data = request.get_json()
    try:
        # Validate required fields
        required = ['activity_name', 'activity_category']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400
            
        scan_data = create_scan(email, data)
        return jsonify(scan_data)
                
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/scans', methods=['GET'])
def get_scan_stats():
    try:
        # Parse query parameters
        min_frequency = request.args.get('min_frequency', type=int)
        max_frequency = request.args.get('max_frequency', type=int)
        activity_category = request.args.get('activity_category')

        stats = get_scan_statistics(
            min_frequency=min_frequency,
            max_frequency=max_frequency,
            activity_category=activity_category
        )

        return jsonify({
            'activities': stats,
            'total_activities': len(stats),
            'cached_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Initialize database when the app starts
init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

