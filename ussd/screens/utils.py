from collections import OrderedDict
from bids.models import Bid

class Fetcher:

	def fetch_bids_menu(self):
		ls = []
		menu = Bid.objects.filter(is_open=True).order_by('-priority').values_list('product__name','code','product')
		ls.extend(((str(i), x) for i,x in enumerate(menu, 1)))
		ls = OrderedDict(ls)
		ls[str(len(ls)+1)] = ('How it works', 'sm.how_it_works')
		ls[str(len(ls)+1)] = ('View Products', 'sm.view')
		ls[str(len(ls)+1)] = ('Customer Care', 'sm.customer_care')
		return ls

	

