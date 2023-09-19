# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import messaging
# from dotenv import load_dotenv
# import os

# dotenv_path = os.path.join('.secrets', '.env')
# load_dotenv(dotenv_path)

# cred = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# credentials = credentials.Certificate(cred)
# default_app = firebase_admin.initialize_app(credentials)

# message = messaging.Message(
#     data={
#         "title": "Hello",
#         "body": "This is a test notification",
#     },
#     token='e1UskxFHSE2yepu2ap_hVT:APA91bHOzcOUnWLOhkJx4J9NTlDiEW4-auKJXJMzVbh52skYZmEXOOmq5zqKRuiwoPYHjxopCTTvuPSdnAKpe-kYO1ZCbHYCkF9Jct-bWEl2Slp_o23oNRlQ2LkBNu1lLIghZrNBus6O',
# )

# response = messaging.send(message)
# print("Successfully sent message:", response)

def notify(user, title, body):
    pass
