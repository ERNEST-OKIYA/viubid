import requests
from django.conf import settings
from db import Db #import even when not using.
from bids.models import InvalidBid,BidEntry
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
        for i_bid in invalid_bids:
            bill_ref_no = helpers.sanitize_billref_no(i_bid.bill_ref_no)
            notes = i_bid.notes
            l_bill_ref_no = i_bid.bill_ref_no
            


            
            try:
                if notes =='Amount less than ticket cost':
                    i_bid.resolved =2
                    i_bid.resolve_notes = "Cannot be resolved. Amount added to wallet."
                    i_bid.save()
                else:
                   
                    digits = re.findall(r"[-+]?\d*\.\d+|\d+",bill_ref_no)
                    bill_ref_extract = bill_ref_no
                    if len(digits)>0:
                        digits = digits[0]
                        bill_ref_extract = bill_ref_no.replace(digits,'')
                   
                    code = helpers.get_bid_code(bill_ref_extract)
                    
                    bid = helpers.get_bid_by_code(code)
                    
                    if bid:
                        
                
                        if len(digits)!=0:
                            amount = float(digits)
                            amount = int(amount)
                        transaction_amount = 20
                        
                        payin = PayIn.objects.filter(bill_reference_number=l_bill_ref_no,msisdn=i_bid.user.phone_number).last()
                        transaction_id = payin.transaction_id
                        source = ''
                        
                        helpers.create_bid_entry(i_bid.user,amount,transaction_id,code,source,bill_ref_no,transaction_amount)
                        print("bid resolved")
                        i_bid.notes = "bid resolved"
                        i_bid.resolved = 1
                        i_bid.save()
                        

                
            except Exception as e:
                print(f'{repr(e)}')
                logger.error('ERROR {}'.format(str(e)))


        time.sleep(1) #wait  seconds before processing again



#runs
run()




