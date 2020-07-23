from celery import Celery
import requests

app = Celery('tasks', broker='amqp://guest@localhost//')


@app.task
def stkpush(payload,headers):
    url = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    r=requests.post(url,json=payload,headers=headers,verify=False)
    rv = r.json()
    print(rv)
    if rv.get('ResultCode')!='0':
        text = "Something is not right"
        # sms.stkpush_down()