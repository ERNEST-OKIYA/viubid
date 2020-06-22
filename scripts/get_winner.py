from db import Db
from factory.helpers import Helpers

helpers = Helpers()

def run():
    bid = helpers.get_active_bid()
    winner = helpers.get_min_unique_bid(bid)

    print("WINNER",winner.bid_entry.user.phone_number)
    print("AMOUNT",winner.amount)

run()