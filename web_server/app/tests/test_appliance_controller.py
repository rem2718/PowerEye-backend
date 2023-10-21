from app.controllers.appliance_controller import *
from app.models.appliance_model import Appliance, ApplianceType, EType
from app.models.user_model import User
import os 
from app import create_app
import pytest

# Fixture to set up the Flask app for testing
@pytest.fixture
def app():
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app()
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

# Test for adding an appliance
def test_add_appliance(client):
    # Create a test user
    user = User(email='test@example.com', password='testpassword', cloud_password='your_cloud_password_here')
    user.save()


    # Define appliance details
    name = "Test Appliance"
    cloud_id = "test-cloud-id"
    type = ApplianceType.COOLER.value

    # Send a POST request to add the appliance
    response = client.post('/add_appliance', json={
        'user_id': str(user.id),
        'name': name,
        'cloud_id': cloud_id,
        'type': type
    })

    # Check if the response status code is 201 (Created)
    assert response.status_code == 201

    # Check if the appliance is added to the user's list of appliances
    user = User.objects.get(id=user.id)
    assert len(user.appliances) == 1

    # Check if the appliance details are correct
    appliance = user.appliances[0]
    assert appliance.name == name
    assert appliance.cloud_id == cloud_id
    assert appliance.type == type

# # Test for switching an appliance
# def test_switch_appliance(client):
#     # Create a test user
#     user = User(email='test@example.com', password='testpassword')
#     user.save()

#     # Create a test appliance
#     appliance = Appliance(
#         name="Test Appliance",
#         type=ApplianceType.COOLER.value,
#         cloud_id="test-cloud-id",
#         e_type=EType.NONE
#     )
#     appliance.save()

#     # Add the appliance to the user's list of appliances
#     user.appliances.append(appliance)
#     user.save()

#     # Send a POST request to switch the appliance
#     response = client.post('/switch_appliance', json={
#         'user_id': str(user.id),
#         'appliance_id': str(appliance.id),
#         'status': True
#     })

#     # Check if the response status code is 200 (OK)
#     assert response.status_code == 200

#     # Check if the appliance status is updated
#     appliance = Appliance.objects.get(id=appliance.id)
#     assert appliance.status == True

# Test for getting the most recent reading of an appliance
def test_get_most_recent_reading(client):
    # Create a test user
    user = User(email='test@example.com', password='testpassword')
    user.save()

    # Create a test appliance
    appliance = Appliance(
        name="Test Appliance",
        type=ApplianceType.COOLER.value,
        cloud_id="test-cloud-id",
        e_type=EType.NONE
    )
    appliance.save()

    # Add the appliance to the user's list of appliances
    user.appliances.append(appliance)
    user.save()

    # Create a test power reading
    power_reading = Power(
        user=user,
        appliances_powers={str(appliance.id): 50}  # Assuming the power is 50 units
    )
    power_reading.save()

    # Send a GET request to get the most recent reading
    response = client.get(f'/get_most_recent_reading?user_id={str(user.id)}&appliance_id={str(appliance.id)}')

    # Check if the response status code is 200 (OK)
    assert response.status_code == 200

    # Check if the response contains the correct power value
    assert response.json['power'] == 50

# # Test for deleting an appliance
# def test_delete_appliance(client):
#     # Create a test user
#     user = User(email='test@example.com', password='testpassword')
#     user.save()

#     # Create a test appliance
#     appliance = Appliance(
#         name="Test Appliance",
#         type=ApplianceType.COOLER.value,
#         cloud_id="test-cloud-id",
#         e_type=EType.NONE
#     )
#     appliance.save()

#     # Add the appliance to the user's list of appliances
#     user.appliances.append(appliance)
#     user.save()

#     # Send a DELETE request to delete the appliance
#     response = client.delete(f'/delete_appliance?user_id={str(user.id)}&appliance_id={str(appliance.id)}')

#     # Check if the response status code is 200 (OK)
#     assert response.status_code == 200

#     # Check if the appliance is marked as deleted
#     appliance = Appliance.objects.get(id=appliance.id)
#     assert appliance.is_deleted == True

#     # Check if the appliance is removed from the user's list of appliances
#     user = User.objects.get(id=user.id)
#     assert len(user.appliances) == 0
