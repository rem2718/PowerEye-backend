from flask import Flask, jsonify, session, request
from dotenv import load_dotenv
import asyncio
import json
import meross
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '.secrets', '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


@app.route('/')
def hello_world():
    async_task_result =  asyncio.run(meross.verify_credentials())
    return jsonify({"message": async_task_result._cloud_creds.token})

# @app.route('/')
# async def hello_world():
#     async_task_result = await meross.verify_credentials()
#     return jsonify({"message": async_task_result})

@app.route('/login', methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['password']
    asyncio.run(meross.verify_credentials(email, password))
    return 'login is done!'

@app.route('/home')
def home():
    return jsonify({"message": asyncio.run(meross.get_status())})


if __name__ == '__main__':
    app.run()