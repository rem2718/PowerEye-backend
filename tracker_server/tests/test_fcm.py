# import os

# from dotenv import load_dotenv
# from unittest.mock import Mock, MagicMock
# import pytest
    
# from app.external_dependencies.fcm import FCM
# from app.types_classes import NotifType

# load_dotenv(os.path.join('.secrets', '.env'))

# @pytest.fixture(scope="module")
# def fcm_instance():
#     CRED = os.getenv('GOOGLE_APPLICATION_CREDENTIALS') 
#     mock_db = Mock()
#     mock_db.get_doc.return_value = 'fhsfc6eZTqGbBA4roX_BTa:APA91bEATox4iW2TJ9XVkWoqG3j3JMkR0eJgLPxWZRkNnPinIxtBJL5pS5-Ho8Xr-BhE-0kI-tA_rIijSZCsZ83CrV2aC0QTNd-OJO981eKC5iQBZW8tPDk6BX7TX0uLm3xj5Y3f8KWM'
#     return FCM(CRED, mock_db)

# @pytest.mark.parametrize(
#     ('type', 'data', 'output'), (
#           (NotifType.CREDS, None, ('Update Your Login', 'Please update your login information for Meross.')),
#           (NotifType.PEAK, {"app_name":'tv'}, ('Peak Usage Alert','Try not to use tv after 5 PM. Click here to turn it off.'))  
#     )
# )
# def test_map_message(fcm_instance, type, data, output):
#     assert fcm_instance.map_message(type, data) == output
    
# def test_notify(fcm_instance):
#     assert 'powereye1-e599e' in fcm_instance.notify('test user', NotifType.PEAK, {'app_name':'tv'})
    
# def test_successful_notification(fcm_instance):
#     user = 'test_user'
#     notification_type = NotifType.CREDS
#     data = {'app_name': 'TestApp'}

#     response = fcm_instance.notify(user, notification_type, data)
#     # You can add assertions here to check if the response is as expected

# def test_map_message(fcm_instance):
#     # Test mapping a notification message based on NotifType.CREDS
#     title, body = fcm_instance.map_message(NotifType.CREDS)
#     assert title == 'Update Your Login'
#     assert body == 'Please update your login information for Meross.'

#     data = {'percentage': 80}
#     title, body = fcm_instance.map_message(NotifType.GOAL, data)
#     assert title == 'Monthly Usage Goal'
#     assert body == "You're close to reaching 80% of your monthly usage goal."

# def test_notify(fcm_instance):
#     # Mock a user and their registration token
#     user = 'test_user_id'
#     mock_token = 'test_registration_token'
#     fcm_instance.db.get_doc.return_value = {'registration_token': mock_token}

#     # Mock the messaging.send method
#     fcm_instance.logger.info = MagicMock()
#     fcm_instance.map_message = MagicMock(return_value=('Test Title', 'Test Body'))
#     fcm_instance.messaging.send = MagicMock(return_value='Test Response')

#     # Call the notify method and check if it works as expected
#     fcm_instance.notify(user, NotifType.PEAK, {'app_name': 'TestApp'})
#     fcm_instance.db.get_doc.assert_called_with('Users', {'_id': user}, {'registration_token': 1})
#     fcm_instance.map_message.assert_called_with(NotifType.PEAK, {'app_name': 'TestApp'})
#     fcm_instance.logger.info.assert_called_with('notify: NotifType.PEAK {\'app_name\': \'TestApp\'}')
#     fcm_instance.messaging.send.assert_called_once()

#     fcm_instance.logger.info.assert_any_call("Notification sent with response: 'Test Response'")
