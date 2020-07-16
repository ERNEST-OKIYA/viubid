from collections import OrderedDict
from bids.models import Bid

class Fetcher:

	def fetch_bids_menu(self):
		ls = []
		menu = Bid.objects.filter(is_open=True).order_by('-closes_at').values_list('product__name','code','product')
		ls.extend(((str(i), x) for i,x in enumerate(menu, 1)))
		ls = OrderedDict(ls)
		return ls

	

