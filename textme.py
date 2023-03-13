""" send myself cellphone text message
Gmail need special verification :-(
import smtplib

def textme(
    gmail_address = 'xxxx@gmail.com',
    gmail_password = 'xxxx',
    text_from = 'Scripts',
    vtext_address = 'xxxx@vtext.com',
    msg = None,
): 
    # Establish a secure session with gmail's outgoing SMTP server using your gmail account
    server = smtplib.SMTP( "smtp.gmail.com", 587 )

    server.starttls()

    server.login( gmail_address, gmail_password )

    # Send text message through SMS gateway of destination number
    server.sendmail( text_from, vtext_address, msg )
       
if __name__ == '__main__':
    textme(msg='text from python (Appriss)')

# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client

# Set environment variables for your credentials
# Read more at http://twil.io/secure
account_sid = "AC7f9040c6cfca9a6d1ce78446ce67fd4d"
auth_token = "9bee9f42f8da37ef7a7c2d3066db18bf"
verify_sid = "VAd75c8c042743a552fe7098f867da0def"
verified_number = "+19498781382"

client = Client(account_sid, auth_token)

verification = client.verify.v2.services(verify_sid) \
  .verifications \
  .create(to=verified_number, channel="sms")
print(verification.status)

otp_code = input("Please enter the OTP:")

verification_check = client.verify.v2.services(verify_sid) \
  .verification_checks \
  .create(to=verified_number, code=otp_code)
print(verification_check.status)
"""
import os
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
if __name__ == '__main__':
    textme(msg='text from python (Appriss)')
