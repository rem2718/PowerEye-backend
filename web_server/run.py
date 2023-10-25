#run.py:
from app import create_app
from app.views.energy_views import app as dummy
import asyncio
from app.utils.cloud_interface import cloud_interface


#cloud interface (merros & tuya)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
cloud = cloud_interface(loop)

if __name__ == '__main__':
    app = create_app()
    app.register_blueprint(dummy)
    app.run()


