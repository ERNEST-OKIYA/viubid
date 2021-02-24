from db import Db
from factory.helpers import Helpers
from messaging.tasks import send_unqiue_bidders_sms

helpers = Helpers()

def run():
    try:
        bid = helpers.get_bid_by_id(id=100)
        winner = helpers.get_min_unique_bid(bid)

        print("WINNER",winner.bid_entry.user.phone_number)
        print("AMOUNT",winner.amount)
        print(f"{winner.bid_entry.user.profile.first_name} - {winner.bid_entry.user.profile.last_name}")
        return send_unqiue_bidders_sms.delay(bid.id,winner.amount,winner.bid_entry.user.profile.first_name)
    
    except Exception as e:
        print(str(e))

run()