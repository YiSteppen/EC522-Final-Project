import sqlite3
import requests
from sqlite3 import Error

def clear_database(database_name):
    try:
        with sqlite3.connect(database_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
            print("All tables have been dropped.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

def create_tables(database_name):
    sql_commands = [
        '''
        CREATE TABLE IF NOT EXISTS user (
            user_id INTEGER PRIMARY KEY,
            user_name TEXT NOT NULL,
            user_password TEXT NOT NULL,
            user_email TEXT NOT NULL UNIQUE
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS authorization (
            auth_email TEXT NOT NULL,
            auth_password TEXT NOT NULL,
            PRIMARY KEY (auth_email)
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS dataupload (
            user_id INTEGER,
            data_id INTEGER PRIMARY KEY,
            train_data TEXT,
            test_data TEXT,
            train_label TEXT,
            test_label TEXT,
            FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS model (
            user_id INTEGER,
            model_id INTEGER PRIMARY KEY,
            model_ver TEXT,
            FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS projects (
            project_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            model_id INTEGER,
            data_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE,
            FOREIGN KEY (model_id) REFERENCES model (model_id) ON DELETE CASCADE,
            FOREIGN KEY (data_id) REFERENCES dataupload (data_id) ON DELETE CASCADE
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS training (
            product_id INTEGER PRIMARY KEY,
            data_id INTEGER,
            training_points TEXT,
            training_parameters TEXT,
            training_result TEXT,
            FOREIGN KEY (data_id) REFERENCES projects (data_id) ON DELETE CASCADE
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS analysis (
            product_id INTEGER PRIMARY KEY,
            model_id INTEGER,
            training_result TEXT,
            test_result TEXT,
            ana_result TEXT,
            FOREIGN KEY (model_id) REFERENCES model (model_id)
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS testing (
            product_id INTEGER PRIMARY KEY,
            data_id INTEGER,
            testing_result TEXT,
            FOREIGN KEY (data_id) REFERENCES projects (data_id) ON DELETE CASCADE
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS publishing (
            user_id INTEGER,
            project_id INTEGER,
            data_id INTEGER,
            ana_result TEXT,
            PRIMARY KEY (user_id, project_id),
            FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE,
            FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE,
            FOREIGN KEY (data_id) REFERENCES dataupload (data_id) ON DELETE CASCADE
        );
        '''
    ]

    conn = sqlite3.connect(database_name)
    c = conn.cursor()

    for command in sql_commands:
        c.execute(command)

    conn.commit()
    conn.close()