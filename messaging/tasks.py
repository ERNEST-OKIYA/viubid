from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from messaging.factory import Message
from django.core.cache import cache
sms = Message()
import logging
from factory.helpers import Helpers
helpers = Helpers()
task_logger = get_task_logger(__name__)
logger = logging.getLogger(__name__)


@shared_task(bind=True,max_retries=3,ignore_results=True)
def send_unqiue_bidders_sms(self,bid_id,winning_value,winner_name):
    try:
        data = helpers.get_unique_bids_by_bid_id(bid_id)
        return sms.unique_not_lowest(data,winning_value,winner_name)
    except Exception as exc:
        task_logger.error(f'ERROR:{repr(exc)}')
		
			


	







