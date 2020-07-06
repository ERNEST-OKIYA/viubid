import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)
DEBUG = settings.DEBUG

app={'key':'9b1e459909484acb90ecfdcbfe01d6da', 
     'secret':'868972b8221744129f50b6b77314b77e',
     'profile_id':'1703051'}
ujumbe_url='https://sms.crossgatesolutions.com/api/v2/sendSms'




class Message:
    
    def bid_entry_message(self,bid_entry):
        product_code = bid_entry.bid.product.code
        product_name = bid_entry.bid.product.name
        product_price = bid_entry.bid.product.price
        
        text = "Congratulations, You have been entered auction bidding for "+\
               "{} {} worth KES {}.\n".format(product_code,
                                        product_name,product_price)+\
               "You can try as many times as you wish."
                  
               
        return self.send(bid_entry.user.phone_number,text)
    
    
    def code_not_found(self,user,code):
        text = "Your product code {} ".format(code)+\
               "Did not match any product on bid. "+\
               "Please check and try again.Your money "+\
               "has been added to your wallet."
               
        return self.send(user.phone_number,text)
    
    def less_amount(self,user):
        text = "The minimum amount for this bid is KES 20. Please send KES 20 to Paybill 153621. Enter your bid value as account Name."
        
        return self.send(user.phone_number,text)
            
    def more_amount(self,user,code,ticket_price,to_wallet):
        text = "The bid ticket price "+\
        	"for poduct with code {} ".format(code)+\
            "is {} ".format(ticket_price)+\
            ".{} Has been added to your wallet.".format(to_wallet)+\
            "You can use it on your next bid."
               
               
               
        return self.send(user.phone_number,text)
    
    def user_bid(self,user,amount,bid_entry,unique):
        product_name = bid_entry.bid.product.name
        product_code = bid_entry.bid.product.code
        if self.isfloat(amount):
            amount = '{0:.2f}'.format(amount)
        if unique:
        
            text = "{}, You have placed a bid of KES {} for ".format(user.profile.first_name,amount)+\
            "{}, We shall notify ".format(product_name)+\
            "you once the bid is closed.You are open to place"+\
            " another successful bid.Your bid is currently Unique! Bid ID {}".format(bid_entry.bid.ref_no)
        else:
            text = "{}, You have placed a bid of KES {} for ".format(user.profile.first_name,amount)+\
            "{}, We shall notify ".format(product_name)+\
            "you once the bid is closed.You are open to place"+\
            " another successful bid.Your bid is currently not Unique! Bid ID {}".format(bid_entry.bid.ref_no)

        return self.send(user.phone_number,text)
    
    def code_not_open(self,user):
        text = "No item is open for bidding at the moment" +\
               " Please check again later for available deals.Your money "+\
               "has been added to your wallet."
               
        return self.send(user.phone_number,text)

    
    def non_unique_bid(self,user,bids):
        for b in bids:
            text = "Sorry {}, {}".format(b.bid_entry.user.profile.first_name,user.profile.first_name)+\
            " has just bid {} on {}.".format(b.amount,b.bid_entry.bid.product.name)+\
            " Your bid is no longer unique."+\
            " Bid again to try and get a Unique Bid. Bid ID: {}".format(b.bid_entry.bid.ref_no)

            logger.info('TEXT {}'.format(text))
            b.non_unique_sms_sent = True
            b.save()
            

            return self.send(b.bid_entry.user.phone_number,text)

               
    
    def send(self,msisdn,message):
        
            payload = dict(sender='QUICKBID',message=message,msisdns=[msisdn])
            url = 'https://app.sasasms.co.ke/api/v1/sms/send/'
        
            try:
                r=requests.post(url,json=payload)
                logger.info('RESPONSE {}'.format(r.json()))
            except Exception as e:
                logger.DEBUG('ERROR {}'.format(str(e)))
            return r.json() or {}

    def isfloat(self,value):
        try:
            float(value)
            return True
        except ValueError:
            return False
