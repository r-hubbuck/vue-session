import os
from twilio.rest import Client

account_sid = 'ACbdf7a37b0a57457cafc0b0175927d273'
auth_token = '0d64723b0d9df97e0721848a4e878caf'
client = Client(account_sid, auth_token)

def send_sms(user_code, phone_number):
    message = client.messages.create(
        body=f'Hi! Your verification code is {user_code}',
        from_='+18658760556',
        to=f'{phone_number}'
    )
    print(message.sid)