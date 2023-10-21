#run.py:
import asyncio
from app import create_app
from cloud_interface import Cloud_interface


if __name__ == '__main__':
    app = create_app()
    app.run()

#cloud interface (merros & tuya)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
cloud = Cloud_interface(loop)
