import sqlite3

def get_db_connection(db_name='database.db'):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(database):
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                request_name TEXT NOT NULL,
                file_reference TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER,
                result REAL,
                FOREIGN KEY (request_id) REFERENCES requests (id)
            )
        ''')
        conn.commit()

def get_results(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.user, r.request_name, r.file_reference, res.result 
        FROM requests r
        JOIN results res ON r.id = res.request_id
    ''')
    results = cursor.fetchall()
    conn.close()

    return [{'user': row[0], 'request_name': row[1], 'file_reference': row[2], 'result': row[3]} for row in results]

def check_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM requests")
    records = cursor.fetchall()
    conn.close()
    return records

def drop_db(db_name='database.db'):
    conn = get_db_connection(db_name)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS requests')
    cursor.execute('DROP TABLE IF EXISTS results')
    conn.commit()
    conn.close()

def clear_db(db_name='database.db'):
    conn = get_db_connection(db_name)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM requests')
    cursor.execute('DELETE FROM results')
    conn.commit()
    conn.close()
