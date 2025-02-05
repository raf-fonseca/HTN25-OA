import sqlite3
from app.graphql.types import User

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