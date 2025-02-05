import sqlite3
from app.graphql.types import User, Scan

def get_all_users():
    with sqlite3.connect('/db/hackers.db') as conn:
        c = conn.cursor()
        c.execute('''
            SELECT name, email, phone, badge_code, updated_at
            FROM hackers
            ORDER BY name
        ''')
        
        return [
            User(
                name=row[0],
                email=row[1],
                phone=row[2],
                badge_code=row[3],
                updated_at=row[4]
            )
            for row in c.fetchall()
        ]

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
            
        return User(
            name=row[0],
            email=row[1],
            phone=row[2],
            badge_code=row[3],
            updated_at=row[4]
        )

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
