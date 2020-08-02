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
                    print('Bill REF NO -->',bill_ref_no)
                    digits = re.findall(r"[-+]?\d*\.\d+|\d+",bill_ref_no)
                    if len(digits)>0:
                        digits = digits[0]
                    bill_ref_extract = bill_ref_no.replace(digits,'')
                    print('Bill Ref No Extract',bill_ref_extract)
                    code = helpers.get_bid_code(bill_ref_extract)
                    print('CODE GOT -->',code)
                    bid = helpers.get_bid_by_code(code)
                    
                    if bid:
                        
                        
                        amount = re.findall(r"[-+]?\d*\.\d+|\d+",bill_ref_no)
                        if len(amount)!=0:
                            amount = amount[0]
                        transaction_amount = 20
                        payin = PayIn.objects.filter(bill_reference_number=bill_ref_no,msisdn=bid.user.phone_number).last()
                        transaction_id = payin.transaction_id
                        print("bid resolved")
                        # helpers.create_bid_entry(bid.user,amount,transaction_id,code,source,bill_ref_no,transaction_amount)
                        

                
            except Exception as e:
                print(f'{repr(e)}')
                logger.error('ERROR {}'.format(str(e)))


        time.sleep(1) #wait  seconds before processing again



#runs
run()




