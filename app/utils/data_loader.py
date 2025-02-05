import sqlite3
import requests

def load_example_data():
    example_data_url = "https://gist.githubusercontent.com/SuperZooper3/685fe234d711a92d4f950bdfbed3bd2c/raw"
    try:
        response = requests.get(example_data_url)
        response.raise_for_status()
        data = response.json()
        
        with sqlite3.connect('/db/hackers.db') as conn:
            c = conn.cursor()
            
            # Clear existing data
            c.execute('DELETE FROM scans')
            c.execute('DELETE FROM hackers')
            c.execute('DELETE FROM activities')
            c.execute('DELETE FROM sqlite_sequence WHERE name IN ("scans", "hackers", "activities")')
            
            # Load activities
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
                    pass
            
            # Load hackers and scans
            for hacker in data:
                try:
                    c.execute('''
                        INSERT INTO hackers (name, email, phone, badge_code)
                        VALUES (?, ?, ?, ?)
                    ''', (hacker['name'], hacker['email'], hacker['phone'], hacker['badge_code']))
                    hacker_id = c.lastrowid
                    
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