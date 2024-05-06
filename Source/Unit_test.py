import pytest
from API import app  # Import the Flask application
import requests
from utility import clear_database, create_tables

# Reset the database before running tests
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    database_path = 'projectdatabase.db'
    
    clear_database(database_path)
    create_tables(database_path)
    
    url = 'http://localhost:5000/create_auth'
    user_data = {
        'auth_email': 'yishen@bu.edu',
        'auth_password': 'password123'
    }
    response = requests.post(url, json=user_data)
    yield 

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_post_user_authorized(client):
    response = client.post('/user', json={
        'user_name': 'Yi Shen',
        'user_password': 'password123',
        'user_email': 'yishen@bu.edu'
    })
    assert response.status_code == 201
    assert 'success' in response.json['status']
    pass

def test_post_user_unauthorized(client):
    response = client.post('/user', json={
        'user_name': 'Yi Shen',
        'user_password': 'incorrectpassword',
        'user_email': 'yishen@bu.edu'
    })
    assert response.status_code == 401
    assert 'error' in response.json
    pass

def test_post_user_already_exists(client):
    response = client.post('/user', json={
        'user_name': 'Yi Shen',
        'user_password': 'password123',
        'user_email': 'yishen@bu.edu'
    })
    assert response.status_code == 409
    assert 'error' in response.json
    pass

def test_sql_injection_attempt_1(client):
    response = client.post('/user', json={
        'user_name': " or ''='",
        'user_password': " or ''='",
        'user_email': " or ''='"
    })
    assert response.status_code == 401, f"Expected 400 Bad Request but got {response.status_code}. SQL injection may be possible."
    assert 'error' in response.json, "Error key expected in response when handling SQL injection."
    pass

def test_sql_injection_attempt_2(client):
    response = client.post('/user', json={
        'user_name': '105; DROP TABLE Suppliers',
        'user_password': '105; DROP TABLE Suppliers',
        'user_email': '105; DROP TABLE Suppliers'
    })
    assert response.status_code == 401, f"Expected 400 Bad Request but got {response.status_code}. SQL injection may be possible."
    assert 'error' in response.json, "Error key expected in response when handling SQL injection."
    pass

