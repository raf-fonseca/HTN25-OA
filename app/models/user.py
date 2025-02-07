class User:
    def __init__(self, name, email, phone, badge_code, updated_at, 
                 is_checked_in=False, scans=None):
        self.name = name
        self.email = email
        self.phone = phone
        self.badge_code = badge_code
        self.updated_at = updated_at
        self.is_checked_in = is_checked_in
        self.scans = scans or []
    
    def to_dict(self):
        return {
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'badge_code': self.badge_code,
            'updated_at': self.updated_at,
            'is_checked_in': self.is_checked_in,
            'scans': [scan.to_dict() for scan in self.scans]
        }

class Scan:
    def __init__(self, activity_name, activity_category, scanned_at):
        self.activity_name = activity_name
        self.activity_category = activity_category
        self.scanned_at = scanned_at
    
    def to_dict(self):
        return {
            'activity_name': self.activity_name,
            'activity_category': self.activity_category,
            'scanned_at': self.scanned_at
        } 