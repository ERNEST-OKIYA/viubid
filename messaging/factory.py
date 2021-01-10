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
		
		text = "Congratulations, You have successfully bid for "+\
			   "{} {} worth KES {}.\n".format(product_code,
										product_name,product_price)+\
			   "Bid more on quickbid.co.ke."
				  
			   
		return self.send(bid_entry.user.phone_number,text)
	
	
	def code_not_found(self,user,code):
		text = "The product code {} you entered ".format(code)+\
			   "did not match any product on bid. "+\
			   "Please check and try again. "+\
			   "visit www.quickbid.co.ke to view available deals."
			   
		return self.send(user.phone_number,text)
	
	def less_amount(self,user,code,to_add,w_balance):
		text = f"The minimum amount required to bid is KES 20.Deposit a minimum of KES 20 to enter your unique bid."
		
		return self.send(user.phone_number,text)
			
	def more_amount(self,user,code,ticket_price,to_wallet):
		text = "The bid price "+\
			"for product with code {} ".format(code)+\
			"is {} ".format(ticket_price)+\
			".{} Has been added to your wallet.".format(to_wallet)+\
			"You can use it on your next bid."     
		# return self.send(user.phone_number,text)
	
	def user_bid(self,user,amount,bid_entry,unique):
		product_name = bid_entry.bid.product.name
		product_code = bid_entry.bid.product.code
		if self.isfloat(amount):
			amount = '{0:.2f}'.format(amount)
		if unique:
		
			text = "Close your Fingers {}! Your Bid of KES {} on ".format(user.profile.first_name,amount)+\
			"{} is CURRENTLY UNIQUE, We shall notify ".format(product_name)+\
			"you once the auction ends if your unique bid will be the lowest."+\
			"Bid ID {}".format(bid_entry.bid.ref_no)
		else:
			text = "Pole {}, Your bid of KES {} on".format(user.profile.first_name,amount)+\
			"{} is NOT UNIQUE, ".format(product_name)+\
			"Try again & Bid on more items on www.quickbid.co.ke. Bid ID {}".format(bid_entry.bid.ref_no)

		return self.send(user.phone_number,text)
	
	def code_not_open(self,user,code):
		text = f"No item with bid code {code} was found." +\
			   " Try again & Bid more products on quickbid.co.ke. "
			   
		return self.send(user.phone_number,text)

	def incorrect_bid_amount(self,phone_number,amount):
		text = f"Sorry, Your Bid amount {amount} is incorrect. Please Enter a value greater than 1 and without decimal points. " +\
			   f"Try again & Bid on more products on www.quickbid.co.ke."
			   
		return self.send(phone_number,text)

	

	def stkpush_down(self,msisdn,text):
		return self.send(msisdn,text)

	
	def non_unique_bid(self,user,bids):
		for b in bids:
			text = "Pole {}, {}".format(b.bid_entry.user.profile.first_name,user.profile.first_name)+\
			" has just bid {} on {}.".format(b.amount,b.bid_entry.bid.product.name)+\
			" Your bid is no longer unique."+\
			" Bid again get a Unique Bid. Bid ID: {}".format(b.bid_entry.bid.ref_no)

			logger.info('TEXT {}'.format(text))
			b.non_unique_sms_sent = True
			b.save()
			

			return self.send(b.bid_entry.user.phone_number,text)

	def incorrect_fomart(self,bill_ref_no,phone_number):
		text = f"The Account number format {bill_ref_no} you entered is incorrect. "+\
				"Please Enter account number in the format BIDCODE followed by your bid value "+\
				"EG if a TV is on auction and your bid amount is 43, Enter TV 43. Bid on more products on www.quickbid.co.ke."

		return self.send(phone_number,text)

	def unique_not_lowest(self,datalist,winning_value,winner_name):
		for item in datalist:
			first_name = item.get('first_name','')
			product = item.get('product')
			amount = item.get('amount')
			phone_number = item.get('msisdn')
			text = f"{first_name}, Bidding on {product} has just been closed.Your bid of KES {amount} was Unique but unfortunately it was not the lowest."+\
					f" The lowest unique bidder was {winner_name} with a bid of KES {winning_value}."+\
					f" visit www.quickbid.co.ke to bid on more products and you may be the next lowest bidder."

			if phone_number in ['254705752962','254717059277','254716179978','254707423381','254722365852']:
				continue

			return self.send(phone_number,text)
			


			   
	
	def send(self,msisdn,message):
		return OutgoingSMS.create(msisdn,message)

	   

	def isfloat(self,value):
		try:
			float(value)
			return True
		except ValueError:
			return False