from unittest.mock import AsyncMock
from datetime import datetime
import os

from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from dotenv import load_dotenv
import pytest
    
from app.external_dependencies.meross_module import Meross

load_dotenv(os.path.join('.secrets', '.env'))

@pytest.fixture
def meross_instance():
    email = os.getenv('TEST_EMAIL')
    meross = Meross({'email': email})
    return meross

@pytest.mark.asyncio            
async def test_daily_update_creds():
    meross_mock = Meross({'email': 'mocked_email@gmail.com'})
    meross_mock.update_creds = AsyncMock()
    
    await meross_mock._daily_update_creds()
    meross_mock.prev = datetime.now() - meross_mock.day
    await meross_mock._daily_update_creds()
    
    meross_mock.update_creds.assert_called_once()
    
@pytest.mark.asyncio            
async def test_meross(meross_instance):
    password = os.getenv('TEST_PASS')
    res = await meross_instance.login(password)
    assert res
    assert not meross_instance.first
    assert meross_instance.loggedin
    assert isinstance(meross_instance.client, MerossHttpClient)
    assert isinstance(meross_instance.manager, MerossManager)
    
    res = await meross_instance.get_devices()
    assert isinstance(res, list)
    if len(res) > 0:
        dev = res[0]
        res = await meross_instance.get_id(dev)
        assert isinstance(res, str)

        on_off, connection_status, power = await meross_instance.get_info(dev)
        assert isinstance(on_off, bool)
        assert isinstance(connection_status, bool)
        assert isinstance(power, float)
        assert power >= 0  
    
    await meross_instance._logout()     