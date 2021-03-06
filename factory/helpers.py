from wallets.models import Transaction,Wallet
from users.models import User,Profile
from wallets.models import Wallet
from messaging.models import OutgoingSMS
from payments.models import RawCheckout,PayIn
from winners.models import Winner
import random
import uuid
import string
from itertools import groupby
from bids.models import BidEntry,UserBid,Bid,InvalidBid,UssdDial
from messaging.factory import Message
from decimal import Decimal
from django.conf import settings
from django.db.models import Min
sms = Message()
import logging
logger = logging.getLogger(__name__)
import re
from products.models import Product
import difflib
from ast import literal_eval
from django.core.exceptions import ObjectDoesNotExist
from bids.models import Advertizer
from django.db.models import Count



DEBUG = settings.DEBUG


class Helpers:

	def get_transaction_id(self):
		return uuid.uuid4().hex

	def is_bid_open(self,bid):

		return bid.is_open

	

	def create_profile(self,user,first_name,middle_name,last_name):
		return Profile.create(user,first_name,middle_name,last_name)


	def get_bonus_balance(self,user):
		return Wallet.objects.get(user=user).bonus

	
	def get_wallet_balance(self,user):
		return Wallet.objects.get(user=user).balance

	def create_wallet(self,user):
		return Wallet.create(user=user)
	def wallet_exists(self,user):
		return Wallet.objects.filter(user=user).exists()
	
	

	def get_bid_ticket_price(self,bid):
		return bid.ticket_price

	def get_user(self,phone_number):
		return User.objects.get(phone_number=phone_number)

	def create_user(self,phone_number):
		char_set = string.ascii_uppercase + string.digits
		password = ''.join(random.sample(char_set*6, 6))
		user = User.objects.create_user(phone_number,password)
		wallet = self.create_wallet(user=user)
		return user

	def deposit(self,user,amount,transaction_id,subject=None):
		subject = None or subject

		Wallet.credit(user,amount)
		return Transaction.record(user,amount,transaction_id,'deposit',subject)

	def reverse(self,user,amount):
		transaction_id = self.get_transaction_id()
		Wallet.credit(user,amount)
		return Transaction.record(user,amount,transaction_id,'reversal')

	

	def adjust_wallet_balance(self,user,bid):
		ticket_price = self.get_ticket_price(bid)
		bonus = Wallet.bonus_balance(user)
		balance = Wallet.wallet_balance(user)
		if balance > 0 and balance >= ticket_price:
			Wallet.debit(user,ticket_price)
			return True
		elif balance > 0 and balance < ticket_price:
			deficit = ticket_price - balance
			if bonus >= deficit:
				Wallet.debit_bonus(user,deficit)
				Wallet.reset_balance(user)
				return True
			elif deficit > bonus:
				return False
		elif balance ==0:
			if bonus >= ticket_price:
				Wallet.debit_bonus(user,ticket_price)
				return True
			elif bonus < ticket_price:
				return False


	def is_first_deposit(self,user):
		if Transaction.objects.filter(user=user).exists():
			return False
		else:
			return True


	def send_sms(self,phone_number,text):

		return OutgoingSMS.create(phone_number,text)

	def checkout(self,user,amount):
		return RawCheckout.create(user,amount)

	def taxfy(self,amount):
		return 0.8 * amount

	def is_taxable(self,amount):
		return amount >= 80 
	
	def get_critical_mass(self,bid):
		return bid.critical_mass
	
	def is_critical_mass_reached(self,bid):
		return bid.is_critical_mass_passed
	def get_min_unique_bid(self,bid):
		# entries = bid.entries.all()
		user_bids = UserBid.objects.filter(bid_entry__bid=bid).filter(amount__gte=1).all()
		sorted_entries = sorted(user_bids, key = lambda e : e.amount)
		for k,g in groupby(sorted_entries,lambda se: se.amount):
			bo = next(g)
			try:
				unique = next(g)
			except:
				return bo
			else:
				continue
		return None
	
	def get_bid_by_code(self,code):
		try:
			return Bid.objects.filter(code=code,is_open=True).last()
		
		# try:
		#     return Bid.objects.get(code=code)
		except ObjectDoesNotExist as e:
			DEBUG and logger.debug('BID  Error ---{}'.format(str(e)))
			return False
	

	def get_active_bid(self):
		
		try:
			return Bid.objects.filter(is_open=True).last()
		except ObjectDoesNotExist:
			return False

	def get_active_bids(self):
		return Bid.active()


	# def create_bid_entry(self,user,amount,transaction_id,code,source):
		
	#     bid = self.get_bid_by_code(code)
	#     amount = Decimal(amount)
	#     if amount < settings.BID_TICKET_COST:
	#         notes = 'Amount less than ticket cost'
	#         InvalidBid.create(user,amount,notes)
	#         return sms.less_amount(user)

	#     if bid:
	#         bid_entry = BidEntry.create(user,bid)
	#         Transaction.record(user,amount,transaction_id,
	#                 'bid ticket',bid_entry)

	#         return self.create_user_bid(user,amount,bid_entry,source)
					
			

	#     else:
	#         sms.code_not_open(user)
	#         self.deposit(user,amount,transaction_id,subject='bid not open')



	def create_bid_entry(self,user,bid_value,transaction_id,code,source,bill_ref_no,amount):
		
		bid = self.get_bid_by_code(code)
		
		amount = Decimal(amount)
		try:
			if bid_value <1:
				return sms.incorrect_bid_amount(user.phone_number,bid_value)

		except Exception as e:
			return sms.incorrect_fomart(bill_ref_no,user.phone_number)
			logger.error(f'{repr(e)}')
			
		w_balance = self.get_wallet_balance(user)
		if bid:
			if amount < settings.BID_TICKET_COST:
				amount_to_add = settings.BID_TICKET_COST - amount 
				if w_balance < amount_to_add:
					self.deposit(user,amount,transaction_id)
					w_balance = self.get_wallet_balance(user)
					amount_to_add = settings.BID_TICKET_COST - w_balance
					sms.less_amount(user,code,amount_to_add,w_balance)
					notes = 'Amount less than ticket cost'
					return InvalidBid.create(user,amount,notes,bill_ref_no)
				else:
					Wallet.debit(user,amount_to_add)
					bid_entry = BidEntry.create(user,bid)
					Transaction.record(user,amount,transaction_id,
								'bid ticket',bid_entry)
					
					return self.create_user_bid(user,bid_value,bid_entry,source,bill_ref_no)
					
				
				
			elif  amount > settings.BID_TICKET_COST:
				over = amount - bid.ticket_price
				self.deposit(user,over,transaction_id,subject='over')
				# sms.more_amount(user,code,bid.ticket_price,over)
				bid_entry = BidEntry.create(user,bid)
				return self.create_user_bid(user,bid_value,bid_entry,source,bill_ref_no)
				
			else:
				bid_entry = BidEntry.create(user,bid)
				Transaction.record(user,amount,transaction_id,
								'bid ticket',bid_entry)
				
				return self.create_user_bid(user,bid_value,bid_entry,source,bill_ref_no)
				
		else:
			notes = 'Bid not found'
			InvalidBid.create(user,bid_value,notes,bill_ref_no)

			sms.code_not_found(user,code)
			return self.deposit(user,amount,transaction_id,subject='bid not found')
				
		
	def user_exists(self,phone_number):
		return User.objects.filter(phone_number=phone_number).exists()
	
	def is_bid_id(self,code):
		
		return isinstance(code,int) and BidEntry.objects.filter(pk=code)\
			.exists()
	
	def get_bid_entry(self,code):
		
		return BidEntry.objects.get(pk=code)
	
	def create_user_bid(self,user,amount,bid_entry,source,bill_ref_no):
		try:
			
			user_bid = UserBid.create(user,bid_entry,amount,source)
			if self.is_bid_unique(bid_entry.bid,amount):
				unique = True
				return sms.user_bid(user,amount,bid_entry,unique)
			else:
				unique = False
				sms.user_bid(user,amount,bid_entry,unique)
				bids = self.get_non_unique_bids(bid_entry.bid,amount,user)
				return sms.non_unique_bid(user,bids)

		except Exception as e:
			
			DEBUG and logger.debug('CREATE BID ERROR Error ---{}'.format(str(e)))
			notes = str(e)
			InvalidBid.create(user,amount,notes,bill_ref_no)
			return None

		

	def validate_bid_amount(self,bill_ref_no):
		if bill_ref_no.isdigit():
			bill_ref_no = Decimal(bill_ref_no)
		elif 'bid' in bill_ref_no:
			bill_ref_no = bill_ref_no.replace('bid','').strip()
			if bill_ref_no.isdigit():
				bill_ref_no = Decimal(bill_ref_no)
			
			else:
				bill_ref_no = None

		return bill_ref_no

	def tare_bill_ref_number(self,bill_ref_no,phone_number):
		try:
			code = None
			user = self.get_user(phone_number)
			bill_ref_no = bill_ref_no.replace(' ','')
			
			if bill_ref_no.isdigit():
				amount = int(bill_ref_no)
				return {'code':'PN','amount':amount,'source':'DIRECT DEPOSIT'}


			if self.isfloat(bill_ref_no):
				amount = Decimal(bill_ref_no)
				logger.info('Amount ---{}'.format(str(amount)))
				
				return {'code':'PN','amount':amount,'source':'DIRECT DEPOSIT'}

			
	
			digits = re.findall(r"(\d+(?:\.\d+)?)",bill_ref_no)
			
	
			
			if len(digits)>0:
				digits = digits[0]

				try:
					amount = int(digits)
				except:
					try:
						amount = float(digits)
						amount = int(amount)

					except ValueError:
						amount = digits.replace("'","")
						return sms.incorrect_bid_amount(phone_number,amount)

				if 'WEB' in bill_ref_no:
					code = bill_ref_no[:2]

				elif 'USSD' in bill_ref_no:
					code = bill_ref_no[:2]
				
				else:

					code = bill_ref_no.replace(digits,'').replace('.','')

				bid = self.get_bid_by_code(code)
				if not bid:
					code = self.get_bid_code(code)
					if not code:
						code = bill_ref_no.replace(digits,'').replace('.','')
		
		

			return {'code':code,'amount':amount,'source':''}
		except Exception as e:
			notes = "Unresolved Bid format"
			InvalidBid.create(user,'',notes,bill_ref_no)
			sms.incorrect_fomart(bill_ref_no,phone_number)
			DEBUG and logger.debug('TARE Error ---{}'.format(str(e)))
			return {'code':'bill_ref_extract','amount':amount,'source':''}
		

			

	
	def is_bid_unique(self,bid,amount):
		entries = UserBid.objects.filter(bid_entry__bid=bid,amount=amount).count()
		if entries > 1:
			return False
		else:
			return True

	def get_non_unique_bids(self,bid,amount,user):
		bids = UserBid.objects.filter(bid_entry__bid = bid, amount = amount,
		non_unique_sms_sent=False)\
			.exclude(bid_entry__user=user)
		return bids

	def record_dials(self,phone_number):
		return UssdDial.create(phone_number)

	def isfloat(self,value):
		try:
			float(value)
			return True
		except ValueError:
			return False

	def available_products(self):
		return list(Product.objects.values_list('name', flat=True))

	def advertizers(self):
		return list(Advertizer.objects.values_list('name', flat=True))

	
	def create_winner(self,user,bid,amount):
		return Winner.create(user,bid,amount)

	def sanitize_billref_no(self,bill_ref_no):
		bill_ref_no = bill_ref_no.upper().replace(',','').replace('SH','').replace('BIDCODE','')\
			.replace('_','').replace('-','').replace('..','').replace('/','').replace('KSH','')\
			.replace('/=','').replace('cents','').replace('+','')
		
		if self.advertizers():
			for a in self.advertizers():
				
				bill_ref_no = bill_ref_no.replace(a.upper(),'')

		

		return bill_ref_no


	def get_bid_code(self,value):
		
		bids = Bid.objects.filter(is_open=True).all()
		for bid in bids:
			lookups = bid.lookups
			if lookups:
				lookups = [x.upper() for x in bid.lookups]
				
				match = difflib.get_close_matches(value.upper(),lookups,n=1)
				
				if match:
					
					return bid.code
				
				continue

		return False

	def get_bid_by_id(self,id):
		try:
			return Bid.objects.get(pk=id)
		
		except ObjectDoesNotExist as e:
			DEBUG and logger.debug('BID  Error ---{}'.format(str(e)))
			return False

	def has_previous_win(self,user_id):
		return 'Yes' if Winner.objects.filter(user__id=user_id).exists() else 'No'


	def get_unique_bids_by_bid_id(self,bid_id):
		datalist = []
		unique_bids = UserBid.objects.filter(bid_entry__bid__id=bid_id).values('amount').annotate(amount_count=Count('amount')).filter(amount_count__lt=2).order_by('amount')
		for ub in unique_bids:
			data = {}
			amount = ub.get('amount')
			entry = UserBid.objects.filter(bid_entry__bid__id=bid_id).get(amount=amount)
			data =dict(first_name=entry.bid_entry.user.profile.first_name,
					
					bid_code =entry.bid_entry.bid.code,
					product=entry.bid_entry.bid.product.name,
					amount=entry.amount,
					msisdn=entry.bid_entry.user.phone_number,
					)
			datalist.append(data)
		
		return datalist
			
	







		
		
		


	









