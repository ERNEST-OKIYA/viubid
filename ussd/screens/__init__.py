from collections import OrderedDict

from flex.ussd.screens import UssdScreen, render_screen


from . import casts
from .mixins import ScreenMixin
# from .helpers import Fetcher
# fetcher = Fetcher()
from factory.helpers import Helpers
helpers = Helpers()


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
		if len(args) > 1 or args[0] not in self.MENU_ITEMS:
			self.error(self.ERRORS.INVALID_CHOICE)
			return self.render_menu()

		opt = self.MENU_ITEMS[args[0]]
		
		return render_screen(opt[1])
		

	def render_menu(self):

		self.nav_menu = None
		active_bid = helpers.get_active_bid()
		self.print("Karibu QuickBid.Bid Low, Win Big!")
		self.print("You could go home with a JUST ARRIVED fully loaded Probox for only KES 20!")
		for k, v in self.MENU_ITEMS.items():
			self.print(str(k) + ':',v[0])
			
		return self.CON

	def render(self, opt=None, *args):
		if opt is not None and not args:
			return self.handle_input(opt)
		if args:
			self.print('Invalid choice.')
		return self.render_menu()














