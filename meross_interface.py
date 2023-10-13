# This file will be moved later on to its correct place
from meross_iot.model.credentials import MerossCloudCreds
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from dotenv import load_dotenv
from flask import session
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '.secrets', '.env')
load_dotenv(dotenv_path)

EMAIL = os.getenv("EMAIL")
PASS = os.getenv("PASS")


async def verify_credentials(email=None, password=None):
    client = await MerossHttpClient.async_from_user_password(email=email, password=password)
    session['token'] = client.cloud_credentials.token
    session['key'] = client.cloud_credentials.key
    session['issued_on'] = client.cloud_credentials.issued_on
    return True

async def get_appliances(): 
    # get smartplugs
    pass

async def switch(appliance, status):
    pass 
    
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())    
# loop = asyncio.get_event_loop()
# loop.run_until_complete(verify_credentials())
# loop.stop()