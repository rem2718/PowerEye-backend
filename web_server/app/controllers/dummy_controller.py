import asyncio
from cloud_interface import Cloud_interface

async def main():
    loop = asyncio.get_running_loop()
    cloud = Cloud_interface(loop)

    # Test the methods or functionality of the Cloud_interface class
    await cloud.connect()
    credentials_valid = await cloud.verify_credentials(username='mayakhalide2001@gmail.com', password='smarthomemaya')

    if credentials_valid:
        print("Credentials are valid.")
    else:
        print("Credentials are invalid.")

if __name__ == '__main__':
    asyncio.run(main())