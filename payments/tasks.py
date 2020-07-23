from celery.utils.log import get_task_logger
from django.conf import settings
from messaging.factory import Message
sms = Message()

logger = get_task_logger(__name__)

@app.task
def stkpush(payload):

    r=requests.post(settings.VARIABLES.get('PAY_URL'),json=payload,headers=headers,verify=False)
    print(r.json())
    if rv.get('ResultCode')!='0':
        text = "Something is not right"
        sms.stkpush_down()

