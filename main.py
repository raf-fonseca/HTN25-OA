from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime
import requests
import json

app = Flask(__name__)

def load_example_data():
    example_data_url = "https://gist.githubusercontent.com/SuperZooper3/685fe234d711a92d4f950bdfbed3bd2c/raw"
    try:
        response = requests.get(example_data_url)
        response.raise_for_status()
        data = response.json()
        
        with sqlite3.connect('/db/hackers.db') as conn:
            c = conn.cursor()
            
            
            c.execute('DELETE FROM scans')
            c.execute('DELETE FROM hackers')
            c.execute('DELETE FROM activities')
            
            # Reset auto-increment counters
            c.execute('DELETE FROM sqlite_sequence WHERE name IN ("scans", "hackers", "activities")')
            
            # Load activities first (no dependencies)
            activities_set = set() # set to avoid duplicates
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
            
            # Load hackers and scans 
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
            print("Example data loaded successfully")
            return True
    except Exception as e:
        print(f"Error loading example data: {e}")
        return False

# Database initialization
def init_db():
    with sqlite3.connect('/db/hackers.db') as conn:
        c = conn.cursor()
        
        # Create hackers table with updated_at field
        c.execute('''
        CREATE TABLE IF NOT EXISTS hackers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            badge_code TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create activities table
        c.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_name TEXT UNIQUE NOT NULL,
            activity_category TEXT NOT NULL,
            is_active BOOLEAN DEFAULT FALSE,
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
        
        # update updated_at timestamp on hacker table when it is updated
        c.execute('''
        CREATE TRIGGER IF NOT EXISTS update_hackers_timestamp 
        AFTER UPDATE ON hackers
        BEGIN
            UPDATE hackers SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = NEW.id;
        END;
        ''')
        
        # update updated_at timestamp on hacker table when a scan is inserted
        c.execute('''
        CREATE TRIGGER IF NOT EXISTS update_hackers_on_scan 
        AFTER INSERT ON scans
        BEGIN
            UPDATE hackers SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = NEW.hacker_id;
        END;
        ''')
        
        # Create indexes
        c.execute('CREATE INDEX IF NOT EXISTS idx_hacker_name ON hackers(name)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_hacker_email ON hackers(email)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_activity_category ON activities(activity_category)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_activity_name ON activities(activity_name)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_scan_time ON scans(scanned_at)')
        
        conn.commit()
        
        # Load example data after initializing the database
        load_example_data()

@app.route('/')
def hello_world():
    return 'Hello, World!'

# Initialize database and load data when the app starts
init_db()

