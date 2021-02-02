from collections import OrderedDict

from flex.ussd.screens import UssdScreen, render_screen
from ast import literal_eval


from . import casts
from .mixins import ScreenMixin
# from .helpers import Fetcher
# fetcher = Fetcher()
from factory.helpers import Helpers
from . utils import Fetcher
helpers = Helpers()
fetcher = Fetcher()


class InitialScreen(UssdScreen, ScreenMixin):

	class Meta:
		label = 'initial'

	def render(self, opt=None, *args):
		helpers.record_dials(self.session.phone_number)
		return render_screen('sm.home')



class HomeScreen(UssdScreen, ScreenMixin):

	MENU_ITEMS = OrderedDict([
		('1', ("Bid Now", "sm.bid_items")),
		('2', ("How it works", "sm.how_it_works")),
		('3', ("View products", "sm.view")),
		('4', ("Customer Care", "sm.customer_care")),
		
	])

	class Meta:
		label = 'home'



	def handle_input(self, *args):
		menu = self.session.ctx.bid_menu
		if len(args) > 1 or args[0] not in menu:
			self.error(self.ERRORS.INVALID_CHOICE)
			return self.render_menu()

		opt = menu[args[0]]
		code = opt[1]
		if code in ['sm.how_it_works','sm.view','sm.customer_care']:
			return render_screen(code)
			
		return render_screen('sm.bid_detail',code=code)

	def render_menu(self):
		self.get_menu()
		menu = self.session.ctx.bid_menu
		self.print('Karibu Quickbid. Bid Low, Win Big')
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














