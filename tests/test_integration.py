"""
Integration Tests for Task Management API
"""
import pytest
import requests
import time
import os

BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')


@pytest.fixture(scope='module')
def api_url():
    """Provide base API URL"""
    return BASE_URL


def wait_for_api(url, timeout=30):
    """Wait for API to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/health")
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    return False


def test_api_health(api_url):
    """Test API health endpoint"""
    if not wait_for_api(api_url):
        pytest.skip("API not available")

    response = requests.get(f"{api_url}/health")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'


def test_create_and_retrieve_task(api_url):
    """Test creating a task and retrieving it"""
    if not wait_for_api(api_url):
        pytest.skip("API not available")

    task_data = {
        'title': 'Integration Test Task',
        'description': 'Created during integration testing',
        'completed': False
    }
    create_response = requests.post(f"{api_url}/api/tasks", json=task_data)
    assert create_response.status_code == 201
    created_task = create_response.json()
    task_id = created_task['id']

    get_response = requests.get(f"{api_url}/api/tasks/{task_id}")
    assert get_response.status_code == 200


def test_update_task_workflow(api_url):
    """Test complete task update workflow"""
    if not wait_for_api(api_url):
        pytest.skip("API not available")

    task_data = {'title': 'Task to Update', 'completed': False}
    create_response = requests.post(f"{api_url}/api/tasks", json=task_data)
    task_id = create_response.json()['id']

    update_data = {'title': 'Updated Task Title', 'completed': True}
    update_response = requests.put(
        f"{api_url}/api/tasks/{task_id}", json=update_data)
    assert update_response.status_code == 200


def test_delete_task_workflow(api_url):
    """Test complete task deletion workflow"""
    if not wait_for_api(api_url):
        pytest.skip("API not available")

    task_data = {'title': 'Task to Delete'}
    create_response = requests.post(f"{api_url}/api/tasks", json=task_data)
    task_id = create_response.json()['id']

    delete_response = requests.delete(f"{api_url}/api/tasks/{task_id}")
    assert delete_response.status_code == 200


def test_list_tasks_integration(api_url):
    """Test listing all tasks"""
    if not wait_for_api(api_url):
        pytest.skip("API not available")

    for i in range(3):
        task_data = {'title': f'Batch Task {i}'}
        requests.post(f"{api_url}/api/tasks", json=task_data)

    response = requests.get(f"{api_url}/api/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list)


def test_error_handling_invalid_task(api_url):
    """Test API error handling"""
    if not wait_for_api(api_url):
        pytest.skip("API not available")

    response = requests.post(f"{api_url}/api/tasks",
                             json={'description': 'No title'})
    assert response.status_code == 400


def test_api_readiness(api_url):
    """Test API readiness endpoint"""
    if not wait_for_api(api_url):
        pytest.skip("API not available")

    response = requests.get(f"{api_url}/ready")
    assert response.status_code == 200
