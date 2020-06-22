import requests
from django.utils import timezone


service_token = 'mc-ussd-user-token-594ffd4f111cg'
ussd_code = '*244*2'

BasUrl='http://196.61.32.218:3000/'

class Resources:

    def url(self,endpoint):
        return BasUrl + endpoint
    def check_account_status(self):
        endpoint='api/ussdaccountcheck'
        payload={
            'service_token':service_token,
            'ussd_code':ussd_code


        }
        url=self.url(endpoint)
        print(url,"URL")
        r=requests.post(url,json=payload)
        print(r.json())

    def register_traffic_url(self):
        endpoint='api/ussdendpoint'

        payload={
            'service_token':service_token,
            'ussd_code':ussd_code,
            'endpoint':'http://138.197.183.103:8001/ussd/gh/mtn/'


        }
        url=self.url(endpoint)
        r=requests.post(url,json=payload)
        print(r.json())

    def client_response(self,dtm=None ,msg='CON Hello, Welcome to Dafabet'):
        endpoint='api/ussdclientresponse'

        payload={
            'service_token':service_token,
            'ussd_code':ussd_code,
            'phone_number':'233244588584',
            'message': '%s \n%s' % (msg, (dtm or timezone.now()).strftime('%Y-%m-%d %H:%M:%S %z'))
        }
        url=self.url(endpoint)
        r=requests.post(url, json=payload)
        rv = r.json()
        return rv