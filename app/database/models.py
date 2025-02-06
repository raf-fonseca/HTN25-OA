import sqlite3
from app.models.user import User, Scan
from datetime import datetime, timedelta

_stats_cache = {
    'data': None,
    'last_updated': None
}

def get_all_users():
    with sqlite3.connect('/db/hackers.db') as conn:
        c = conn.cursor()
        c.execute('''
            SELECT name, email, phone, badge_code, updated_at
            FROM hackers
            ORDER BY name
        ''')
        
        users = []
        for row in c.fetchall():
            user = User(
                name=row[0],
                email=row[1],
                phone=row[2],
                badge_code=row[3],
                updated_at=row[4]
            )
            user.scans = get_user_scans(user.email)
            users.append(user)
        
        return users

def get_user_by_email(email):
    with sqlite3.connect('/db/hackers.db') as conn:
        c = conn.cursor()
        c.execute('''
            SELECT name, email, phone, badge_code, updated_at
            FROM hackers
            WHERE email = ?
        ''', (email,))
        
        row = c.fetchone()
        if row is None:
            return None
        
        user = User(
            name=row[0],
            email=row[1],
            phone=row[2],
            badge_code=row[3],
            updated_at=row[4]
        )
        user.scans = get_user_scans(email)
        return user

# Helper function to get user scans when getting users 
def get_user_scans(email):
    with sqlite3.connect('/db/hackers.db') as conn:
        c = conn.cursor()
        c.execute('''
            SELECT a.activity_name, a.activity_category, s.scanned_at
            FROM scans s
            JOIN activities a ON s.activity_id = a.id
            JOIN hackers h ON s.hacker_id = h.id
            WHERE h.email = ?
            ORDER BY s.scanned_at
        ''', (email,))
        
        return [
            Scan(
                activity_name=row[0],
                activity_category=row[1],
                scanned_at=row[2]
            )
            for row in c.fetchall()
        ]

def update_user(email, data):
    with sqlite3.connect('/db/hackers.db') as conn:
        c = conn.cursor()
        
        # Prevent email updates
        if 'email' in data:
            raise ValueError("Email cannot be changed")
        
        update_fields = []
        params = []
        
        if 'name' in data:
            update_fields.append('name = ?')
            params.append(data['name'])
            
        if 'phone' in data:
            update_fields.append('phone = ?')
            params.append(data['phone'])
            
        if 'badge_code' in data:
            # First check if the new badge code is not assigned to another user
            c.execute('SELECT id FROM hackers WHERE badge_code = ?', (data['badge_code'],))
            if c.fetchone() is not None:
                raise ValueError(f"Badge code {data['badge_code']} is already in use")
                
            update_fields.append('badge_code = ?')
            params.append(data['badge_code'])
            
        if not update_fields:
            return get_user_by_email(email)
            
        params.append(email)
        
        # Start transaction
        c.execute('BEGIN TRANSACTION')
        try:
            query = f'''
                UPDATE hackers 
                SET {', '.join(update_fields)}
                WHERE email = ?
            '''
            c.execute(query, params)
            
            if c.rowcount == 0:
                raise ValueError(f"No user found with email {email}")
                
            c.execute('''
                SELECT name, email, phone, badge_code, updated_at
                FROM hackers
                WHERE email = ?
            ''', (email,))
            
            row = c.fetchone()
            conn.commit()
            
            user = User(
                name=row[0],
                email=row[1],
                phone=row[2],
                badge_code=row[3],
                updated_at=row[4]
            )
            user.scans = get_user_scans(email)
            return user
            
        except Exception as e:
            conn.rollback()
            raise e

def create_scan(email, data):
    with sqlite3.connect('/db/hackers.db') as conn:
        c = conn.cursor()
        
        # Get hacker_id
        c.execute('SELECT id FROM hackers WHERE email = ?', (email,))
        hacker = c.fetchone()
        if not hacker:
            raise ValueError('User not found')
        
        # Start transaction
        c.execute('BEGIN TRANSACTION')
        try:
            # Get or create activity
            c.execute('''
                INSERT INTO activities (activity_name, activity_category)
                VALUES (?, ?)
                ON CONFLICT (activity_name) DO UPDATE SET
                activity_category = excluded.activity_category
                RETURNING id
            ''', (data['activity_name'], data['activity_category']))
            
            activity_id = c.fetchone()[0]
            
            # Check for duplicate scan
            c.execute('''
                SELECT scanned_at 
                FROM scans 
                WHERE hacker_id = ? AND activity_id = ? 
                AND date(scanned_at) = date('now')
            ''', (hacker[0], activity_id))
            
            if c.fetchone():
                raise ValueError(f"User already scanned for {data['activity_name']} today")
            
            # Create scan with current timestamp
            c.execute('''
                INSERT INTO scans (hacker_id, activity_id, scanned_at)
                VALUES (?, ?, datetime('now'))
                RETURNING scanned_at
            ''', (hacker[0], activity_id))
            
            scanned_at = c.fetchone()[0]
            
            conn.commit()
            
            return {
                'activity_name': data['activity_name'],
                'activity_category': data['activity_category'],
                'scanned_at': scanned_at
            }
            
        except Exception as e:
            conn.rollback()
            raise e

