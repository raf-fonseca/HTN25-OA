TRIGGERS = [
    '''
    CREATE TRIGGER IF NOT EXISTS update_hackers_timestamp 
    AFTER UPDATE ON hackers
    BEGIN
        UPDATE hackers SET updated_at = CURRENT_TIMESTAMP 
        WHERE id = NEW.id;
    END;
    ''',
    '''
    CREATE TRIGGER IF NOT EXISTS update_hackers_on_scan 
    AFTER INSERT ON scans
    BEGIN
        UPDATE hackers SET updated_at = CURRENT_TIMESTAMP 
        WHERE id = NEW.hacker_id;
    END;
    '''
] 