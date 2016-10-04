from twilio.rest import TwilioRestClient


def load_twilio_config():
    twilio_number = '+13103128668'
    twilio_account_sid = 'ACcfa45113ae5bfb96fb78afe54c8a9075'
    twilio_auth_token = '358d0dd19d428769ae97cf99388d62e4'
    return (twilio_number, twilio_account_sid, twilio_auth_token)


class MessageClient(object):
    def __init__(self):
        (twilio_number, twilio_account_sid,
            twilio_auth_token) = load_twilio_config()

        self.twilio_number = twilio_number
        self.twilio_client = TwilioRestClient(
            twilio_account_sid,
            twilio_auth_token
        )

    def send_message(self, body, to):
        self.twilio_client.messages.create(
            body=body, to=to, from_=self.twilio_number
        )
