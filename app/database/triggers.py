TRIGGERS = [
    '''
    CREATE TRIGGER IF NOT EXISTS update_hackers_timestamp 
    AFTER UPDATE ON hackers
    BEGIN
        UPDATE hackers SET updated_at = strftime('%Y-%m-%dT%H:%M:%S', datetime('now', '-5 hours')) || '-05:00'
        WHERE id = NEW.id;
    END;
    ''',
    '''
    CREATE TRIGGER IF NOT EXISTS update_hackers_on_scan 
    AFTER INSERT ON scans
    BEGIN
        UPDATE hackers SET updated_at = strftime('%Y-%m-%dT%H:%M:%S', datetime('now', '-5 hours')) || '-05:00'
        WHERE id = NEW.hacker_id;
    END;
    '''
] 