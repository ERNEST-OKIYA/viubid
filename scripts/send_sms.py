import requests
from django.conf import settings
from db import Db #import even when not using.
from messaging.models import OutgoingSMS
import logging
logger = logging.getLogger(__name__)
DEBUG = settings.DEBUG
import time




def run():
    ROWS_SELECTION_LIMIT=50
    RESPONSE_ACCEPTED='ACCEPTED'
    RESPONSE_FAILED='FAILED'




    while True:
        #get un processed deposits for processing

        messages=OutgoingSMS.get_unprocessed(limit=ROWS_SELECTION_LIMIT)
        for msg in messages:
            message = msg.text
            msisdn = msg.phone_number


            try:
                payload = dict(sender='QUICKBID',message=message,msisdns=[msisdn])
                url = 'https://app.sasasms.co.ke/api/v1/sms/send/'
                r=requests.post(url,json=payload,timeout=3)
                
                rv = r.json()
                print(rv)
                
                msg.success = rv.get('success')
                msg.identifier = rv.get('identifier')
                msg.status = 1
                msg.status_reason = "Message sent to API"
                msg.save()
              
            except requests.exceptions.Timeout:
                msg.status =2
                msg.status_reason = "Timeout"
                msg.save()

            except requests.exceptions.ConnectionError:
                
                msg.status_reason='ConnectionError'
                msg.status =2
                msg.save()

            except simplejson.scanner.JSONDecodeError:
    
                msg.status_reason='JSONDecodeError'
                msg.status =2
                msg.save()
            
            except Exception as e:
                msg.status_reason= str(e)
                msg.status =2
                msg.save()
                logger.DEBUG('ERROR {}'.format(str(e)))


        time.sleep(1) #wait  seconds before processing again



#runs
run()




