#run.py:
import asyncio
from app import create_app
from app.utils.cloud_interface import Cloud_interface
#chatgpt
from flask import Flask

#cloud interface (merros & tuya)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
cloud = Cloud_interface(loop)

# create a global variable to store the cloud object so controllers can use it
global cloud_obj
cloud_obj = cloud

#chatgpt
app = Flask(__name__)

if __name__ == '__main__':
    app = create_app()
    app.run()


