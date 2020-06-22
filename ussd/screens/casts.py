from collections import OrderedDict

from flex.ussd.screens import UssdScreen, render_screen

from .mixins import ScreenMixin
from django.conf import settings
from factory.helpers import Helpers
import requests
from requests.auth import HTTPBasicAuth

from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
helpers = Helpers()


class BidScreen(UssdScreen, ScreenMixin):

	
	class Meta:
		label = 'bid'



	def handle_input(self, opt):
		if opt.isdigit():
			bid_amount = opt
			self.stkpush(bid_amount)
			self.print('Enter your Mpesa PIN in the next prompt to complete.')
			self.print('If no prompt appears, send KES 20 to PB 825440 Acc No. is your bid Amount')
			return self.CON

		elif int(opt) < 1:
			self.print('Please Enter a Bid Amount Value greater than 1')
			return self.render_menu()
		else:
			self.print("Invalid Bid Amount.")
			return self.render_menu()

	def render_menu(self):
		active_bid = helpers.get_active_bid()
		self.print(active_bid.product.name)
		self.print(active_bid.product.description)
		self.print('Bid closes at {}'.format(active_bid.closes_at.strftime("%d/%m/%Y %H:%M")))
		self.print('Enter your bid Amount:')
		
			
		return self.CON

	def render(self, opt=None, *args):
		if opt is not None and not args:
			return self.handle_input(opt)
		if args:
			self.print('Invalid choice.')
		return self.render_menu()

	def stkpush(self,amount):
		active_bid = helpers.get_active_bid()
		bid_code = active_bid.code
		access_token = self.generate_token()
		source = 'USSD'
		headers={"Authorization":"Bearer %s" % access_token}

		payload = {
				"BusinessShortCode": settings.VARIABLES.get('BUSINESS_SHORTCODE'),
				"Password": settings.VARIABLES.get('PASSWORD'),
				"Timestamp": "20171012092847",
				"TransactionType": "CustomerPayBillOnline",
				"Amount": 20,
				"PartyA": self.session.phone_number,
				"PartyB": settings.VARIABLES.get('BUSINESS_SHORTCODE'),
				"PhoneNumber": self.session.phone_number,
				"CallBackURL": settings.VARIABLES.get('DEFAULTCALLBACKURL'),
				"AccountReference": bid_code + ' ' + amount + ' ' + source,
				"TransactionDesc": 'SokoMiaUSSD'
		}

		print(payload)

		response = requests.post(settings.VARIABLES.get('PAY_URL'),json=payload,headers=headers,verify=False)
		rv = response.json()
		

	def generate_token(self):

		consumer_key = settings.VARIABLES.get('CONSUMER_KEY')
		consumer_secret = settings.VARIABLES.get('CONSUMER_SECRET')
		r = requests.get(settings.VARIABLES.get('TOKEN_URL'), auth=HTTPBasicAuth(consumer_key, consumer_secret))
		token=r.json()
		print(token)
		
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

		self.print("You have a Question or need Help? Contact us on 0720796582.")
		
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

		self.print("Visit www.sokomia.com to view this {} and more products on Auction.".format(product_name))
		
		return self.CON

	def render(self, opt=None, *args):
		if opt is not None and not args:
			return self.handle_input(opt)
		if args:
			self.print('Invalid choice.')
		return self.render_menu()



