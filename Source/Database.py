import sqlite3

# Connect to the database
conn = sqlite3.connect('mydatabase.db')
c = conn.cursor()

# Create the table
c.execute('''
CREATE TABLE user (
    user_id INTEGER PRIMARY KEY,
    user_email TEXT NOT NULL UNIQUE,
    user_name TEXT NOT NULL,
    user_password TEXT NOT NULL,
);
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

c = conn.cursor()
c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='user';")
print(c.fetchone())

# Get detailed information about the table columns
c.execute("PRAGMA table_info('user');")
columns = c.fetchall()
for column in columns:
    print(column)

# Close the connection
conn.close()