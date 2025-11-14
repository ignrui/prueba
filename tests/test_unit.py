"""
Unit Tests for Task Management API
"""
from app import app, db, Task
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


@pytest.fixture
def sample_task(client):
    """Create a sample task for testing"""
    with app.app_context():
        task = Task(
            title='Test Task',
            description='This is a test task',
            completed=False
        )
        db.session.add(task)
        db.session.commit()
        return task.id


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'


def test_readiness_check(client):
    """Test readiness check endpoint"""
    response = client.get('/ready')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ready'


def test_get_tasks_empty(client):
    """Test getting tasks when database is empty"""
    response = client.get('/api/tasks')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_create_task(client):
    """Test creating a new task"""
    task_data = {
        'title': 'New Task',
        'description': 'Task description',
        'completed': False
    }
    response = client.post('/api/tasks', json=task_data)
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == task_data['title']


def test_create_task_without_title(client):
    """Test creating a task without required title"""
    task_data = {'description': 'Task without title'}
    response = client.post('/api/tasks', json=task_data)
    assert response.status_code == 400


def test_get_task_by_id(client, sample_task):
    """Test getting a specific task by ID"""
    response = client.get(f'/api/tasks/{sample_task}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == sample_task


def test_get_nonexistent_task(client):
    """Test getting a task that doesn't exist"""
    response = client.get('/api/tasks/9999')
    assert response.status_code == 404


def test_update_task(client, sample_task):
    """Test updating an existing task"""
    update_data = {
        'title': 'Updated Task',
        'completed': True
    }
    response = client.put(f'/api/tasks/{sample_task}', json=update_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == update_data['title']


def test_delete_task(client, sample_task):
    """Test deleting a task"""
    response = client.delete(f'/api/tasks/{sample_task}')
    assert response.status_code == 200

    # Verify task is deleted
    response = client.get(f'/api/tasks/{sample_task}')
    assert response.status_code == 404


def test_task_model_to_dict(client):
    """Test Task model to_dict method"""
    with app.app_context():
        task = Task(
            title='Model Test',
            description='Testing model conversion',
            completed=True
        )
        db.session.add(task)
        db.session.commit()

        task_dict = task.to_dict()
        assert 'id' in task_dict
        assert task_dict['title'] == 'Model Test'
