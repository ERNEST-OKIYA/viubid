from collections import OrderedDict

from flex.ussd.screens import UssdScreen, render_screen

from .mixins import ScreenMixin
from django.conf import settings
from factory.helpers import Helpers
import requests
from . utils import Fetcher
from requests.auth import HTTPBasicAuth
from ast import literal_eval
from functools import lru_cache
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
helpers = Helpers()
fetcher = Fetcher()


class BidItemScreen(UssdScreen, ScreenMixin):

	
	class Meta:
		label = 'bid_items'


	def handle_input(self, *args):
		menu = self.session.ctx.bid_menu
		if len(args) > 1 or args[0] not in menu:
			self.error(self.ERRORS.INVALID_CHOICE)
			return self.render_menu()

		opt = menu[args[0]]
		code = opt[1]
		return render_screen('sm.bid',code=code)

	def render_menu(self):
		self.get_menu()
		menu = self.session.ctx.bid_menu
		self.print('Select product to bid')
		for k, v in menu.items():
			self.print(str(k) + ':',v[0])
			
		return self.CON

	def get_menu(self):
		menu = fetcher.fetch_bids_menu()
		self.session.ctx.bid_menu = menu
		
	def render(self, opt=None, *args):
		if opt is not None and not args:
			return self.handle_input(opt)
		if args:
			self.print('Invalid choice.')
		return self.render_menu()

	

class BidScreen(UssdScreen, ScreenMixin):

	
	class Meta:
		label = 'bid'

	def handle_input(self, opt):
		try:
			value = literal_eval(opt)
		except:
			self.print ("Invalid bid amount.Please enter a number greater than 1")
			self.print('Enter Correct Bid Amount')
			return self.CON
			
		if isinstance(value,float):
			self.print(f"{value} is Invalid.Please enter a number without cents.Did you mean {int(value)}?")
			self.print('Enter Correct Bid Amount')
			return self.CON

		else:
			self.print('Enter your Mpesa PIN in the next prompt to complete')
			self.stkpush(value)
			self.nav_menu = None
			return self.END
		return render_screen('sm.bid')
	
	def render_menu(self):

		bid = self.get_bid()
		product = bid.product 
		self.print(product.name)
		self.print("RRP:",product.price)
		self.print("Closes at:",self.bid_closes_at(bid))
		self.print('Enter your Bid Amount')
		return self.CON

	def bid_closes_at(self,bid):
		return self.format_date(bid.closes_at)

	def get_bid(self):
		code = self.state.code
		return helpers.get_bid_by_code(code)



	def render(self, opt=None, *args):
		if opt is not None and not args:
			return self.handle_input(opt)
		if args:
			self.print('Invalid choice.')
		return self.render_menu()

	def stkpush(self,amount):
		access_token = self.generate_token()
		source = 'USSD'
		code = self.state.code
		headers={"Authorization":"Bearer %s" % access_token}

		payload = {
				"BusinessShortCode": settings.VARIABLES.get('BUSINESS_SHORTCODE'),
				"Password": settings.VARIABLES.get('PASSWORD'),
				"Timestamp": settings.VARIABLES.get('Timestamp'),
				"TransactionType": "CustomerPayBillOnline",
				"Amount": 20,
				"PartyA": self.session.phone_number,
				"PartyB": settings.VARIABLES.get('BUSINESS_SHORTCODE'),
				"PhoneNumber": self.session.phone_number,
				"CallBackURL": settings.VARIABLES.get('DEFAULTCALLBACKURL'),
				"AccountReference": code + ' ' + str(amount),
				"TransactionDesc": 'QuickBidUSSD'
		}


		response = requests.post(settings.VARIABLES.get('PAY_URL'),json=payload,headers=headers,verify=False)
		
		rv = response.json()
		
	@lru_cache
	def generate_token(self):

		consumer_key = settings.VARIABLES.get('CONSUMER_KEY')
		consumer_secret = settings.VARIABLES.get('CONSUMER_SECRET')
		r = requests.get(settings.VARIABLES.get('TOKEN_URL'), auth=HTTPBasicAuth(consumer_key, consumer_secret))
		token=r.json()
		
		
		return token.get('access_token')





class HowScreen(UssdScreen, ScreenMixin):

	
	class Meta:
		label = 'how_it_works'



	def handle_input(self, *args):
		pass
	def render_menu(self):

		self.print("If your bid is the lowest and MOST UNIQUE, you will purchase the item for the bid amount.")
		self.print("Items are delivered nationwide free of charge.")
			
		return self.CON

	def render(self, opt=None, *args):
		if opt is not None and not args:
			return self.handle_input(opt)
		if args:
			self.print('Invalid choice.')
		return self.render_menu()



class CareScreen(UssdScreen, ScreenMixin):

	
	class Meta:
		label = 'customer_care'



	def handle_input(self, *args):
		pass
	def render_menu(self):

		self.print("You have a Question or need Help? Contact us on 0712345678.")
		
		return self.CON

	def render(self, opt=None, *args):
		if opt is not None and not args:
			return self.handle_input(opt)
		if args:
			self.print('Invalid choice.')
		return self.render_menu()



class ViewProductScreen(UssdScreen, ScreenMixin):

	
	class Meta:
		label = 'view'



	def handle_input(self, *args):
		pass
	def render_menu(self):
		active_bid = helpers.get_active_bid()
		product_name = active_bid.product.name

		self.print("Visit www.quickbid.co.ke to view this {} and more products on Auction.".format(product_name))
		
		return self.CON

	def render(self, opt=None, *args):
		if opt is not None and not args:
			return self.handle_input(opt)
		if args:
			self.print('Invalid choice.')
		return self.render_menu()



