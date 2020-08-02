import requests
import logging
from django.conf import settings
from .models import OutgoingSMS

logger = logging.getLogger(__name__)
DEBUG = settings.DEBUG



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
        text = "The product code {} you entered ".format(code)+\
               "did not match any product on bid. "+\
               "Please check and try again.Your money "+\
               "has been added to your wallet.visit www.quickbid.co.ke to view available deals."
               
        return self.send(user.phone_number,text)
    
    def less_amount(self,user,code,to_add,w_balance):
        text = f"The minimum amount required to bid is KES 20.Your wallet balance is KES {w_balance} "+\
            f" Please deposit KES {to_add} to Paybill 4032353 to bid."
        
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
    
    def code_not_open(self,user,code):
        text = f"No item with bid code {code} was found." +\
               " Your money has been added to your wallet.go to www.quickbid.co.ke to view available deals."
               
        return self.send(user.phone_number,text)

    def incorrect_bid_amount(self,phone_number,amount):
        text = f"The minimum bid Amount is KES 1. {amount} is incorrect." +\
               " Your money has been added to your wallet." +\
               f" {settings.USSDADVIDE}. Visit www.quickbid.co.ke to view available deals."
               
        return self.send(phone_number,text)

    def stkpush_down(self,msisdn,text):
        return self.send(msisdn,text)

    
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

    def incorrect_fomart(self,bill_ref_no,phone_number):
        text = f"The Account number format {bill_ref_no} you entered is incorrect. "+\
                "Please Enter account number in the format BIDCODE followed by your bid value "+\
                "EG if a TV is on offer and your bid amount is 43, Enter TV 43.visit www.quickbid.co.ke to view available deals."

        return self.send(phone_number,text)

               
    
    def send(self,msisdn,message):
        return OutgoingSMS.create(msisdn,message)

       

    def isfloat(self,value):
        try:
            float(value)
            return True
        except ValueError:
            return False
