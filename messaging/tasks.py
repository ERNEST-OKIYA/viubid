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


@shared_task(bind=True,max_retries=3,ignore_result=True)
def send_unqiue_bidders_sms(self,bid_id,winning_value,winner_name):
	try:
		data = helpers.get_unique_bids_by_bid_id(bid_id)
		for item in data:
			first_name = item.get('first_name','')
			product = item.get('product')
			amount = item.get('amount')
			phone_number = item.get('msisdn')
			text = f"{first_name}, Bidding on {product} has just been closed.Your bid of KES {amount} was Unique but unfortunately it was not the lowest."+\
					f" The lowest unique bidder was {winner_name} with a bid of KES {winning_value}."+\
					f" visit www.quickbid.co.ke to bid on more products and you may be the next lowest bidder."

			if phone_number in ['254705752962','254717059277','254716179978','254707423381','254722365852']:
				continue
		sms.send(phone_number,text)
	except Exception as exc:
		task_logger.error(f'ERROR:{repr(exc)}')
		
			


	







