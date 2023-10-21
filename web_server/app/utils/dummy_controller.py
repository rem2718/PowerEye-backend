from flask import Flask, session
import asyncio
from cloud_interface import verify_credentials

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, Flask!"

@app.route('/verify')
def verify():
    asyncio.run(run_verification())
    return "Verification completed"

async def run_verification():
    credentials_valid = await verify_credentials(email='mayakhalide2001@gmail.com', password='smarthomemaya')
    if credentials_valid:
        print("Credentials are valid.")
    else:
        print("Credentials are invalid.")

async def main():
    await run_verification()

if __name__ == '__main__':
    app.run()