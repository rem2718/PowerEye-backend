import os

from dotenv import load_dotenv
from unittest.mock import Mock
import pytest

from app.external_dependencies.fcm import FCM
from app.types_classes import NotifType

load_dotenv(os.path.join('.secrets', '.env'))

@pytest.fixture(scope="module")
def my_fcm():
    CRED = os.getenv('GOOGLE_APPLICATION_CREDENTIALS') 
    mock_db = Mock()
    mock_db.get_doc.return_value = 'fhsfc6eZTqGbBA4roX_BTa:APA91bEATox4iW2TJ9XVkWoqG3j3JMkR0eJgLPxWZRkNnPinIxtBJL5pS5-Ho8Xr-BhE-0kI-tA_rIijSZCsZ83CrV2aC0QTNd-OJO981eKC5iQBZW8tPDk6BX7TX0uLm3xj5Y3f8KWM'
    return FCM(CRED, mock_db)

@pytest.mark.parametrize(
    ('type', 'data', 'output'), (
          (NotifType.CREDS, None, ('Update Your Login', 'Please update your login information for Meross.')),
          (NotifType.PEAK, {"app_name":'tv'}, ('Peak Usage Alert','Try to use tv after 5 PM. Click here to turn it off.'))  
    )
)
def test_map_message(my_fcm, type, data, output):
    assert my_fcm.map_message(type, data) == output
    
def test_notify(my_fcm):
    assert 'powereye1-e599e' in my_fcm.notify('test user', NotifType.PEAK, {'app_name':'tv'})