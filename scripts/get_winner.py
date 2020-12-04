from db import Db
from factory.helpers import Helpers

helpers = Helpers()

def run():
    bid = helpers.get_bid_by_id(id=32)
    winner = helpers.get_min_unique_bid(bid)

    print("WINNER",winner.bid_entry.user.phone_number)
    print("AMOUNT",winner.amount)
    print(f"{winner.bid_entry.user.profile.first_name} - {winner.bid_entry.user.profile.last_name}")

run()