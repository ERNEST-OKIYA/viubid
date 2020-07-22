import requests
from django.conf import settings
from db import Db #import even when not using.
from bids.models import InvalidBid
import re
import time
import difflib
from factory.helpers import Helpers
from bids.models import Bid
from payments.models import PayIn
helpers = Helpers()
import logging
logger = logging.getLogger(__name__)
DEBUG = settings.DEBUG


def run():
    ROWS_SELECTION_LIMIT=50
    RESPONSE_ACCEPTED='ACCEPTED'
    RESPONSE_FAILED='FAILED'




    while True:
        #get un processed deposits for processing

        invalid_bids=InvalidBid.get_unprocessed(limit=ROWS_SELECTION_LIMIT)
        for bid in invalid_bids:
            bill_ref_no = bid.bill_ref_no
            notes = bid.notes
            


            
            try:
                if notes =='Amount less than ticket cost':
                    bid.resolved =2
                    bid.resolve_notes = "Cannot be resolved. Amount added to wallet."
                    bid.save()
                else:
                    bill_ref_extract = bill_ref_no.replace(re.findall(r"[-+]?\d*\.\d+|\d+",bill_ref_no)[0],'')
                    products = helpers.available_products()
                    product = difflib.get_close_matches(bill_ref_extract,products)
                    print(product)
                    if len(product)==1:
                        bid_p = Bid.objects.filter(product__name=product[0]).last()
                        code = bid_p.code
                        source = 'DIRECT DEPOSIT'
                        amount = re.findall(r"[-+]?\d*\.\d+|\d+",bill_ref_no)[0]
                        transaction_amount = 20
                        payin = PayIn.objects.filter(bill_reference_number=bill_ref_no,msisdn=bid.user.phone_number).last()
                        transaction_id = payin.transaction_id
                        bid.resolved =1
                        bid.resolve_notes = "Successfully Resolved"
                        bid.save()
                        helpers.create_bid_entry(bid.user,amount,transaction_id,code,source,bill_ref_no,transaction_amount)
                        

                
            except Exception as e:
                bid.resolve_notes= str(e)
                bid.resolved =2
                bid.save()
                logger.error('ERROR {}'.format(str(e)))


        time.sleep(1) #wait  seconds before processing again



#runs
run()




