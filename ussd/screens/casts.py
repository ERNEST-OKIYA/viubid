from collections import OrderedDict

from flex.ussd.screens import UssdScreen, render_screen

from .mixins import ScreenMixin
from django.conf import settings
from factory.helpers import Helpers
from django.core.cache import cache
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
		return render_screen('sm.bid_detail',code=code)

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

	


class BidDetailScreen(UssdScreen, ScreenMixin):

	MENU_ITEMS = OrderedDict([
		('1', ("Place Bid", "sm.bid")),
		('2', ("Cancel", "sm.rate")),
		
		
	])

	
	class Meta:
		label = 'bid_detail'

	def handle_input(self, *args):
		if len(args) > 1 or args[0] not in self.MENU_ITEMS:
			self.error(self.ERRORS.INVALID_CHOICE)
			return self.render_menu()

		opt = self.MENU_ITEMS[args[0]]
		
		return render_screen(opt[1],code=self.state.code)
		
	def render_menu(self):

		bid = self.get_bid()
		product = bid.product 
		self.print(product.name)
		self.print(f'RRP: {bid.product.price}')
		self.print('Save: Up to 99%')
		self.print("Ticket price:",bid.ticket_price)
		self.print("ENDS AT:",self.bid_closes_at(bid))
		for k, v in self.MENU_ITEMS.items():
			self.print(str(k) + ':',v[0])
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


class BidScreen(UssdScreen, ScreenMixin):
	
	class Meta:
		label = 'bid'

	nav_menu = None

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
			return render_screen('sm.confirm_payment',code=self.state.code,bid_amount=value)
	
	def render_menu(self):
		self.print('Enter your Bid Amount(The Lowest UNIQUE Bid Amount WINS the BID)')
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





class PaymentConfirmationScreen(UssdScreen, ScreenMixin):

	MENU_ITEMS = OrderedDict([
		('1', ("Proceed", "sm.checkout")),
		('2', ("Cancel", "sm.rate")),
		
		
	])
	class Meta:
		label = 'confirm_payment'


	def handle_input(self, *args):
		if len(args) > 1 or args[0] not in self.MENU_ITEMS:
			self.error(self.ERRORS.INVALID_CHOICE)
			return self.render_menu()

		opt = self.MENU_ITEMS[args[0]]
		
		return render_screen(opt[1],code=self.state.code,bid_amount=self.state.bid_amount)
			
	def render_menu(self):
		bid = self.get_bid()
		ticket_price = bid.ticket_price
		self.print(f'KES {ticket_price} will be Deducted from your Mpesa.')
		for k, v in self.MENU_ITEMS.items():
			self.print(str(k) + ':',v[0])

		return self.CON

	def render(self, opt=None, *args):
		if opt is not None and not args:
			return self.handle_input(opt)
		if args:
			self.print('Invalid choice.')
		return self.render_menu()

	def get_bid(self):
		code = self.state.code
		return helpers.get_bid_by_code(code)


class CheckoutScreen(UssdScreen, ScreenMixin):

	
	class Meta:
		label = 'checkout'

	def handle_input(self, opt):
		pass
	
	def render_menu(self):
		self.nav_menu = None
		bid = self.get_bid()
		product = bid.product.name
		bid_amount = self.state.bid_amount
		self.state.ticket_price = bid.ticket_price
		self.print(f'Enter your MPESA PIN in the next prompt to place your Bid of KES {bid_amount} on {product}')
		self.stkpush()

		
		return self.END


	def get_bid(self):
		code = self.state.code
		return helpers.get_bid_by_code(code)



	def render(self, opt=None, *args):
		if opt is not None and not args:
			return self.handle_input(opt)
		if args:
			self.print('Invalid choice.')
		return self.render_menu()

	def stkpush(self):
		access_token = cache.get('access_token')
		if not access_token:
			access_token = self.generate_token()
		source = 'USSD'
		code = self.state.code
		headers={"Authorization":"Bearer %s" % access_token}

		payload = {
				"BusinessShortCode": settings.VARIABLES.get('BUSINESS_SHORTCODE'),
				"Password": settings.VARIABLES.get('PASSWORD'),
				"Timestamp": settings.VARIABLES.get('Timestamp'),
				"TransactionType": "CustomerPayBillOnline",
				"Amount": int(self.state.ticket_price),
				"PartyA": self.session.phone_number,
				"PartyB": settings.VARIABLES.get('BUSINESS_SHORTCODE'),
				"PhoneNumber": self.session.phone_number,
				"CallBackURL": settings.VARIABLES.get('DEFAULTCALLBACKURL'),
				"AccountReference": code + '#' + str(self.state.bid_amount) + '#' + source,
				"TransactionDesc": 'chezachiniUSSD'
		}


		response = requests.post(settings.VARIABLES.get('PAY_URL'),json=payload,headers=headers,verify=False)
		
		rv = response.json()
		
	def generate_token(self):

		consumer_key = settings.VARIABLES.get('CONSUMER_KEY')
		consumer_secret = settings.VARIABLES.get('CONSUMER_SECRET')
		r = requests.get(settings.VARIABLES.get('TOKEN_URL'), auth=HTTPBasicAuth(consumer_key, consumer_secret))
		token=r.json()
		access_token = token.get('access_token')
		cache.set('access_token',access_token,1700)
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

		self.print("You have a Question or need Help? Contact us on 0753146246.")
		
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

class UssdSurveyScreen(UssdScreen, ScreenMixin):

	class Meta:
		label = 'survey'



	def handle_input(self, opt):
		try:
			rate = self.state.rate
			helpers.record_survey(phone_number=self.session.phone_number,rate=rate,text=opt)
			return render_screen('sm.quit')
		except:
			return render_screen('sm.quit')

	def render_menu(self):
		if int(self.state.rate) <=5:
			self.print(f'You rated us {self.state.rate}/10')
			self.print("Please take a moment to tell us how we can serve you better")
		else:
			self.print(f'You rated us {self.state.rate}/10.We are glad you are enjoying Quick Bid.')
			self.print("Is there anything we can do to serve you better?")

		
		return self.CON

	def render(self, opt=None, *args):
		if opt is not None and not args:
			return self.handle_input(opt)
		if args:
			self.print('Invalid choice.')
		return self.render_menu()


class ServiceRateScreen(UssdScreen, ScreenMixin):

	class Meta:
		label = 'rate'



	def handle_input(self, opt):
		if not opt.isdigit():
			self.print("Please Enter a number between 1 and 10")
			return self.render_menu()
		else:
			self.state.rate = opt
			return render_screen('sm.survey',rate=opt)

	def render_menu(self):

		self.print("In a Scale of 1 to 10, How do you rate our services?")
		
		return self.CON

	def render(self, opt=None, *args):
		if opt is not None and not args:
			return self.handle_input(opt)
		if args:
			self.print('Invalid choice.')
		return self.render_menu()



class QuitScreen(UssdScreen, ScreenMixin):

	
	class Meta:
		label = 'quit'



	def handle_input(self, *args):
		pass
	def render_menu(self):
		

		self.print("Thank you for being part of the Bid Low, Win Big Community.Hope to see you soon.")
		
		return self.CON

	def render(self, opt=None, *args):
		if opt is not None and not args:
			return self.handle_input(opt)
		if args:
			self.print('Invalid choice.')
		return self.render_menu()