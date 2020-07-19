from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import PayIn,CheckoutResponse
from django.conf import settings
import json
from users.models import Profile
from factory.helpers import Helpers
helpers = Helpers()
import logging
logger = logging.getLogger(__name__)
from functools import lru_cache

DEBUG = settings.DEBUG
import requests
from requests.auth import HTTPBasicAuth

from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Create your views here.

def standardize_msisdn(msisdn):
	if msisdn.startswith('0'):
		return '254' + msisdn.lstrip('0').replace(' ','').strip()
	else:
		return msisdn.replace(' ','').strip()

@lru_cache
def generate_token():

	consumer_key = settings.VARIABLES.get('CONSUMER_KEY')
	consumer_secret = settings.VARIABLES.get('CONSUMER_SECRET')
	

	r = requests.get(settings.VARIABLES.get('TOKEN_URL'), auth=HTTPBasicAuth(consumer_key, consumer_secret))
	
	token=r.json()
	
	return token.get('access_token')

class Payins(View):

	def post(self,request):
	   
	 
		data = json.loads(request.body.decode('utf-8'))
		transaction_id = data.get('TransID')
		transaction_time = data.get('TransTime')
		transaction_amount = data.get('TransAmount')
		bill_reference_number = data.get('BillRefNumber')
		org_account_balance = data.get('OrgAccountBalance')
		msisdn = data.get('MSISDN')
		first_name = data.get('FirstName')
		middle_name = data.get('MiddleName')
		last_name = data.get('LastName')

		if PayIn.objects.filter(transaction_id=transaction_id).exists():
			return JsonResponse({'status':'Record already Exists'})

		else:

			PayIn.create(transaction_id,transaction_time,\
				transaction_amount,bill_reference_number,\
					org_account_balance,msisdn,first_name,\
						middle_name,last_name)
			
			if not helpers.user_exists(msisdn):
				user = helpers.create_user(msisdn)
				helpers.create_profile(user,first_name,middle_name,last_name)
				
			else:
				user = helpers.get_user(msisdn)
				if not Profile.objects.filter(user=user).exists():
					helpers.create_profile(user,first_name,middle_name,last_name)

				
			items = helpers.tare_bill_ref_number(bill_reference_number,msisdn)
			if isinstance(items,dict):
				code = items.get('code')
				amount = items.get('amount')
				source = items.get('source')
				helpers.create_bid_entry(user,amount,transaction_id,code,source)
			
			else:
				logger.debug('Invalid bid amount {}'.format(bill_reference_number))
			

		return JsonResponse({'status':'Accepted'})


	def get(self,request):
		return JsonResponse({'HTTP_STATUS':403})

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)





class CheckoutResult(View):
	def post(self, request):
		data = request.body.decode('utf-8')

		CheckoutResponse.objects.create(response=data)
		return JsonResponse({'status': 'created'})

	def get(self, request):
		return JsonResponse({'status': None})

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super(CheckoutResult, self).dispatch(request, *args, **kwargs)

class Checkouts(View):
	response = {}
	def post(self,request):
		if request.is_ajax():
			phone_number = standardize_msisdn(request.POST.get('phone_number'))
			bid_value =  request.POST.get('bid_value')
			bid_code = request.POST.get('bid_code')
			access_token = generate_token()
			active_bid = helpers.get_bid_by_code(bid_code)
			source = 'WEB'
			

			headers={"Authorization":"Bearer %s" % access_token}
			

			payload = {
					"BusinessShortCode": settings.VARIABLES.get('BUSINESS_SHORTCODE'),
					"Password": settings.VARIABLES.get('PASSWORD'),
					"Timestamp": settings.VARIABLES.get('Timestamp'),
					"TransactionType": "CustomerPayBillOnline",
					"Amount": 20,
					"PartyA": phone_number,
					"PartyB": settings.VARIABLES.get('BUSINESS_SHORTCODE'),
					"PhoneNumber": phone_number,
					"CallBackURL": settings.VARIABLES.get('DEFAULTCALLBACKURL'),
					"AccountReference": bid_code + ' ' + bid_value + ' ' + source,
					"TransactionDesc": 'QuickBid'
			}

			
			try:

				response=requests.post(settings.VARIABLES.get('PAY_URL'),json=payload,headers=headers,verify=False)
				
				
				
				self.response['phone_number']= phone_number
				self.response['product']= active_bid.product.name
				self.response['bid_value']= bid_code


				return JsonResponse(self.response,status=200)

			except Exception as e:
				DEBUG and logger.debug(str(e))
				self.response['error']= "* Oops, there was an error placing your bid, Please try again Later."
				return JsonResponse(self.response,status=200)

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)



