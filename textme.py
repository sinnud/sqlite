""" Create account using gmail on twilio with trial version
The trial version with $15.50 balance free. There will be monthly charge from this balance.
It may not work when balance go to ZERO.
VENV need to install moduel `twilio` before run the code here.
"""
from twilio.rest import Client # pip install twilio

def textme(msg = None,):

    account_sid = 'AC7f9040c6cfca9a6d1ce78446ce67fd4d'
    auth_token = '9bee9f42f8da37ef7a7c2d3066db18bf'
    from_number = '+12082950575'
    to_number ='+19498781382'
    body = msg
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=body,
        from_=from_number,
        to=to_number
    )