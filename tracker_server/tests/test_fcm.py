import pytest
from unittest.mock import MagicMock
from your_module import FCM
from app.types_classes import NotifType

@pytest.fixture
def fcm_instance():
    # Mock Firebase credentials for testing
    cred = 'test_credentials.json'
    db = MagicMock()
    return FCM(cred, db)

def test_map_message(fcm_instance):
    # Test mapping a notification message based on NotifType.CREDS
    title, body = fcm_instance.map_message(NotifType.CREDS)
    assert title == 'Update Your Login'
    assert body == 'Please update your login information for Meross.'

    # Test mapping a notification message based on NotifType.GOAL with custom data
    data = {'percentage': 80}
    title, body = fcm_instance.map_message(NotifType.GOAL, data)
    assert title == 'Monthly Usage Goal'
    assert body == "You're close to reaching 80% of your monthly usage goal."

def test_notify(fcm_instance):
    # Mock a user and their registration token
    user = 'test_user_id'
    mock_token = 'test_registration_token'
    fcm_instance.db.get_doc.return_value = {'registration_token': mock_token}

    # Mock the messaging.send method
    fcm_instance.logger.info = MagicMock()
    fcm_instance.map_message = MagicMock(return_value=('Test Title', 'Test Body'))
    fcm_instance.messaging.send = MagicMock(return_value='Test Response')

    # Call the notify method and check if it works as expected
    fcm_instance.notify(user, NotifType.PEAK, {'app_name': 'TestApp'})
    fcm_instance.db.get_doc.assert_called_with('Users', {'_id': user}, {'registration_token': 1})
    fcm_instance.map_message.assert_called_with(NotifType.PEAK, {'app_name': 'TestApp'})
    fcm_instance.logger.info.assert_called_with('notify: NotifType.PEAK {\'app_name\': \'TestApp\'}')
    fcm_instance.messaging.send.assert_called_once()

    # Check if the notification response is logged
    fcm_instance.logger.info.assert_any_call("Notification sent with response: 'Test Response'")

# You can add more test cases as needed

# from unittest.mock import Mock
# from app.external_dependencies.FCM import FCM
# from app.types_classes import NotifType


# # Mock the database connection (you might need to use a testing library like unittest.mock)
# class MockDB:
#     def get_doc(self, collection, filter, projection):
#         # Implement your own mock for database retrieval
#         return {"registration_token": "mock_token"}

# def fcm_instance():
#     # Create and return an instance of FCM with a mock database
#     db = MockDB()
#     return FCM('path_to_firebase_credentials.json', db)

# def test_successful_notification(fcm_instance):
#     user = 'test_user'
#     notification_type = NotifType.CREDS
#     data = {'app_name': 'TestApp'}

#     response = fcm_instance.notify(user, notification_type, data)
#     # You can add assertions here to check if the response is as expected

# def test_invalid_user(fcm_instance):
#     # Test the scenario where an invalid user is provided
#     pass

# def test_different_notification_types(fcm_instance):
#     # Test each notification type (CREDS, DISCONNECTION, GOAL, PEAK, PHANTOM, BASELINE)
#     pass

# def test_custom_data(fcm_instance):
#     # Test with custom data and ensure the title and body include the data
#     pass

# def test_database_retrieval(fcm_instance):
#     # Test if the database retrieval works correctly
#     pass

# def test_invalid_firebase_credentials(fcm_instance):
#     # Test how the class handles cases with missing or invalid Firebase credentials
#     pass

# def test_logging(fcm_instance):
#     # Test if the class logs the notifications correctly
#     pass

# def test_response_handling(fcm_instance):
#     # Test how the class handles different response statuses from Firebase
#     pass

# def test_edge_cases(fcm_instance):
#     # Test edge cases, such as very long data values, empty data, and special characters
#     pass

# def test_exception_handling(fcm_instance):
#     # Test how the class handles exceptions that might be raised during the notification process
#     pass

