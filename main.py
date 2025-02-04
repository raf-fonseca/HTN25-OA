from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime
import requests
import json

app = Flask(__name__)

# Load initial data from example data URL
def load_example_data():
    example_data_url = "https://gist.githubusercontent.com/SuperZooper3/685fe234d711a92d4f950bdfbed3bd2c/raw"
    try:
        response = requests.get(example_data_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        
        with sqlite3.connect('/db/hackers.db') as conn:
            c = conn.cursor()
            
            # Clear existing data
            c.execute('DELETE FROM scans')
            c.execute('DELETE FROM hackers')
            c.execute('DELETE FROM activities')
            
            # Reset auto-increment counters
            c.execute('DELETE FROM sqlite_sequence WHERE name IN ("scans", "hackers", "activities")')
            
            # Load activities first (since they're referenced by scans)
            activities_set = set()
            for hacker in data:
                for scan in hacker.get('scans', []):
                    activities_set.add((
                        scan['activity_name'],
                        scan['activity_category']
                    ))
            
            for activity_name, activity_category in activities_set:
                try:
                    c.execute('''
                        INSERT INTO activities (activity_name, activity_category)
                        VALUES (?, ?)
                    ''', (activity_name, activity_category))
                except sqlite3.IntegrityError:
                    pass  # Skip if activity already exists
            
            # Load hackers and their scans
            for hacker in data:
                try:
                    # Insert hacker
                    c.execute('''
                        INSERT INTO hackers (name, email, phone, badge_code)
                        VALUES (?, ?, ?, ?)
                    ''', (hacker['name'], hacker['email'], hacker['phone'], hacker['badge_code']))
                    hacker_id = c.lastrowid
                    
                    # Insert their scans
                    for scan in hacker.get('scans', []):
                        c.execute('SELECT id FROM activities WHERE activity_name = ?', 
                                (scan['activity_name'],))
                        activity_id = c.fetchone()[0]
                        
                        c.execute('''
                            INSERT INTO scans (hacker_id, activity_id, scanned_at)
                            VALUES (?, ?, ?)
                        ''', (hacker_id, activity_id, scan['scanned_at']))
                        
                except sqlite3.IntegrityError as e:
                    print(f"Error inserting hacker {hacker['email']}: {e}")
                    continue
            
            conn.commit()
            return True
    except Exception as e:
        print(f"Error loading example data: {e}")
        return False

# Database initialization
def init_db():
    with sqlite3.connect('/db/hackers.db') as conn:
        c = conn.cursor()
        
        # Create hackers table
        c.execute('''
        CREATE TABLE IF NOT EXISTS hackers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            badge_code TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create activities table
        c.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_name TEXT UNIQUE NOT NULL,
            activity_category TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create scans table
        c.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hacker_id INTEGER NOT NULL,
            activity_id INTEGER NOT NULL,
            scanned_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hacker_id) REFERENCES hackers (id),
            FOREIGN KEY (activity_id) REFERENCES activities (id)
        )
        ''')
        
        # Create indexes
        c.execute('CREATE INDEX IF NOT EXISTS idx_hacker_name ON hackers(name)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_hacker_email ON hackers(email)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_activity_category ON activities(activity_category)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_activity_name ON activities(activity_name)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_scan_time ON scans(scanned_at)')
        
        conn.commit()

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/load-data', methods=['POST'])
def load_data():
    success = load_example_data()
    if success:
        return jsonify({'message': 'Example data loaded successfully'}), 200
    else:
        return jsonify({'error': 'Failed to load example data'}), 500

# Initialize database when the app starts
init_db()

