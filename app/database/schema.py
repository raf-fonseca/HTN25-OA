import sqlite3
from app.database.triggers import TRIGGERS
from app.utils.data_loader import load_example_data
from datetime import datetime

# Database table definitions
HACKERS_TABLE = '''
CREATE TABLE IF NOT EXISTS hackers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    badge_code TEXT UNIQUE,
    updated_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', datetime('now', '-5 hours')) || '-05:00'),
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', datetime('now', '-5 hours')) || '-05:00')
)
'''

ACTIVITIES_TABLE = '''
CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_name TEXT UNIQUE NOT NULL,
    activity_category TEXT NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', datetime('now', '-5 hours')) || '-05:00')
)
'''

SCANS_TABLE = '''
CREATE TABLE IF NOT EXISTS scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hacker_id INTEGER NOT NULL,
    activity_id INTEGER NOT NULL,
    scanned_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', datetime('now', '-5 hours')) || '-05:00'),
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', datetime('now', '-5 hours')) || '-05:00'),
    FOREIGN KEY (hacker_id) REFERENCES hackers (id),
    FOREIGN KEY (activity_id) REFERENCES activities (id)
)
'''

CHECKED_IN_TABLE = '''
CREATE TABLE IF NOT EXISTS checked_in_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hacker_id INTEGER UNIQUE NOT NULL,
    FOREIGN KEY (hacker_id) REFERENCES hackers (id)
)
'''

def init_db():
    with sqlite3.connect('/db/hackers.db') as conn:
        c = conn.cursor()
        
        # Create tables
        c.execute(HACKERS_TABLE)
        c.execute(ACTIVITIES_TABLE)
        c.execute(SCANS_TABLE)
        c.execute(CHECKED_IN_TABLE)
        
        # Create triggers
        for trigger in TRIGGERS:
            c.execute(trigger)
        
        # Create indexes
        c.execute('CREATE INDEX IF NOT EXISTS idx_hacker_name ON hackers(name)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_hacker_email ON hackers(email)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_activity_category ON activities(activity_category)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_activity_name ON activities(activity_name)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_scan_time ON scans(scanned_at)')
        
        conn.commit()
        
        # Load example data
        load_example_data() 