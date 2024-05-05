import sqlite3

def create_database():
    # Connect to a new or existing database
    conn = sqlite3.connect('projectdatabase.db')
    cursor = conn.cursor()

    # Create a new 'user' table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
        userid INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        password TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE
    );
    ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()
    print("Database and 'user' table created successfully.")