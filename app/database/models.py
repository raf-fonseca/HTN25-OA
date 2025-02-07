import sqlite3
from app.models.user import User, Scan
from datetime import datetime, timedelta

_stats_cache = {
    'data': None,
    'last_updated': None
}

def get_all_users(checked_in=None, order_by='name'):
    with sqlite3.connect('/db/hackers.db') as conn:
        c = conn.cursor()
        
        # Base query - determine checked_in status from scan existence
        query = '''
            SELECT h.name, h.email, h.phone, h.badge_code, h.updated_at,
                   CASE WHEN COUNT(s.id) > 0 THEN TRUE ELSE FALSE END as is_checked_in,
                   COUNT(s.id) as scan_count
            FROM hackers h
            LEFT JOIN scans s ON h.id = s.hacker_id
            GROUP BY h.id
        '''
        
        # Add checked_in filter if specified
        if checked_in is not None:
            query += f' HAVING is_checked_in = {1 if checked_in else 0}'
                
        query += f' ORDER BY {order_by}'
        
        c.execute(query)
        
        users = []
        for row in c.fetchall():
            user = User(
                name=row[0],
                email=row[1],
                phone=row[2],
                badge_code=row[3],
                updated_at=row[4],
                is_checked_in=bool(row[5])
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
            # Check if the badge code is different from user's current one
            c.execute('SELECT badge_code FROM hackers WHERE email = ?', (email,))
            current_badge = c.fetchone()
            if current_badge and current_badge[0] != data['badge_code']:
                # Only check for conflicts if badge code is actually changing
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
                updated_at=row[4],
                is_checked_in=True  # Set to True since they're registered
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
                VALUES (?, ?, strftime('%Y-%m-%dT%H:%M:%S', datetime('now', '-5 hours')) || '-05:00')
            ''', (hacker[0], activity_id))
            
            conn.commit()
            
            # Return complete user data including new scan
            return get_user_by_email(email).to_dict()
            
        except Exception as e:
            conn.rollback()
            raise e


def get_scan_statistics(min_frequency=None, max_frequency=None, activity_category=None, cache_duration_minutes=5):
    """Get scan statistics with caching and filtering"""
    global _stats_cache
    
    # Check if we have valid cached data
    now = datetime.utcnow() - timedelta(hours=5)  # Convert to EST
    if (_stats_cache['data'] is not None and 
        _stats_cache['last_updated'] is not None and 
        now - _stats_cache['last_updated'] < timedelta(minutes=cache_duration_minutes)):
        data = _stats_cache['data']
        cached_at = _stats_cache['last_updated']
    else:
        # Cache miss or expired, fetch new data
        with sqlite3.connect('/db/hackers.db') as conn:
            c = conn.cursor()
            
            # Get base statistics
            c.execute('''
                SELECT 
                    a.activity_name,
                    a.activity_category,
                    COUNT(s.id) as scan_count
                FROM activities a
                LEFT JOIN scans s ON a.id = s.activity_id
                GROUP BY a.id, a.activity_name, a.activity_category
                ORDER BY scan_count DESC, a.activity_name
            ''')
            
            data = [
                {
                    'activity_name': row[0],
                    'activity_category': row[1],
                    'scan_count': row[2]
                }
                for row in c.fetchall()
            ]
            
            # Update cache with new data and timestamp
            _stats_cache['data'] = data
            _stats_cache['last_updated'] = now
            cached_at = now
    
    # Apply filters to cached data
    filtered_data = data
    
    if min_frequency is not None:
        filtered_data = [d for d in filtered_data if d['scan_count'] >= min_frequency]
        
    if max_frequency is not None:
        filtered_data = [d for d in filtered_data if d['scan_count'] <= max_frequency]
        
    if activity_category is not None:
        filtered_data = [d for d in filtered_data if d['activity_category'] == activity_category]
    
    # Return with EST timezone indicator
    return filtered_data, cached_at.strftime('%Y-%m-%dT%H:%M:%S') + '-05:00'

def checkin_user_db(data):
    with sqlite3.connect('/db/hackers.db') as conn:
        c = conn.cursor()
        try:
            # Check if user already exists
            c.execute('SELECT email FROM hackers WHERE email = ?', (data['email'],))
            if c.fetchone():
                raise ValueError(f"User with email {data['email']} is already registered")

            # Check if badge code is already in use
            c.execute('SELECT email FROM hackers WHERE badge_code = ?', (data['badge_code'],))
            if c.fetchone():
                raise ValueError(f"Badge code {data['badge_code']} is already in use")

            # Create new user
            c.execute('''
                INSERT INTO hackers (name, email, phone, badge_code)
                VALUES (?, ?, ?, ?)
            ''', (data['name'], data['email'], data.get('phone'), data['badge_code']))
            
            conn.commit()

            # Get the newly created user
            c.execute('''
                SELECT name, email, phone, badge_code, updated_at
                FROM hackers
                WHERE email = ?
            ''', (data['email'],))
            
            row = c.fetchone()
            user = User(
                name=row[0],
                email=row[1],
                phone=row[2],
                badge_code=row[3],
                updated_at=row[4],
                is_checked_in=True
            )
            
            # Return list with single user for consistent API response
            return [user]
            
        except Exception as e:
            conn.rollback()
            raise e

def checkout_user_db(email):
    with sqlite3.connect('/db/hackers.db') as conn:
        c = conn.cursor()
        try:
            # Check if user exists
            c.execute('SELECT id FROM hackers WHERE email = ?', (email,))
            if not c.fetchone():
                raise ValueError('User not found')
            
            # Get all users with the checked out user having is_checked_in=False
            c.execute('''
                SELECT name, email, phone, badge_code, updated_at
                FROM hackers
                ORDER BY updated_at DESC
            ''')
            
            row = c.fetchone()
            user = User(
                name=row[0],
                email=row[1],
                phone=row[2],
                badge_code=row[3],
                updated_at=row[4],
                is_checked_in=False
            )
            
            # Return list with single user for consistent API response
            return [user]
            
            
        except Exception as e:
            conn.rollback()
            raise e
