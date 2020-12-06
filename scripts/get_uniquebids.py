from db import Db
from bids.models import UserBid
from django.db.models import Count


def get_uniques(bid_id):

    unique_bids = UserBid.objects.filter(bid_entry__bid__id=bid_id).values('amount').annotate(amount_count=Count('amount')).filter(amount_count__lt=2)
    for entry in unique_bids:
        print(entry.bid_entry.bid.user.profile.first_name,entry.bid_entry.bid.user.profile.last_name,entry.bid_entry.bid.code,entry.bid_entry.bid.product.name,entry.amount)



get_uniques(32)