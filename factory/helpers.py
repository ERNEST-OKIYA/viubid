from wallets.models import Transaction,Wallet
from users.models import User,Profile
from wallets.models import Wallet
from messaging.models import OutgoingSMS
from payments.models import RawCheckout,PayIn
import random
import uuid
import string
from itertools import groupby
from bids.models import BidEntry,UserBid,Bid,InvalidBid,UssdDial
from messaging.factory import Message
from decimal import Decimal
from django.conf import settings
sms = Message()
import logging
logger = logging.getLogger(__name__)

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
        user_bids =UserBid.objects.filter(bid_entry__bid=bid).filter(amount__gte=1).all()
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
        from django.core.exceptions import ObjectDoesNotExist
        try:
            return Bid.objects.get(code=code)
        except ObjectDoesNotExist as e:
            DEBUG and logger.debug('BID  Error ---{}'.format(str(e)))
            return False
    

    def get_active_bid(self):
        from django.core.exceptions import ObjectDoesNotExist
        try:
            return Bid.objects.filter(is_open=True).last()
        except ObjectDoesNotExist:
            return False


    def create_bid_entry(self,user,amount,transaction_id,code,source):
        # if code:

        #     bid = self.get_bid_by_code(code)
        
        # else:
        bid = self.get_active_bid()
        amount = Decimal(amount)
        if bid:
            bid_entry = BidEntry.create(user,bid)
            Transaction.record(user,amount,transaction_id,
                    'bid ticket',bid_entry)

            return self.create_user_bid(user,amount,bid_entry,source)
                    
            

        else:
            sms.code_not_open(user)
            self.deposit(user,amount,transaction_id,subject='bid not open')



    # def create_bid_entry(self,code,user,amount,transaction_id):
    #     bid = self.get_bid_by_code(code)
    #     amount = Decimal(amount)
    #     if bid is not False and self.is_bid_open(bid):
            
    #         if bid:
    #             if bid.ticket_price > amount:
    #                 amount_to_add = bid.ticket_price - amount
    #                 if self.get_wallet_balance(user) < amount_to_add:

    #                     self.deposit(user,amount,transaction_id)
    #                     sms.less_amount(user,code,amount_to_add)
    #                 else:
    #                     Wallet.debit(user,amount_to_add)
    #                     bid_entry = BidEntry.create(user,bid)
    #                     Transaction.record(user,amount,transaction_id,
    #                                 'bid ticket',bid_entry)
                    
    #                     sms.bid_entry_message(bid_entry)
    #                     return bid_entry
                        
                    
                    
    #             elif bid.ticket_price < amount:
    #                 over = amount - bid.ticket_price
    #                 self.deposit(user,over,transaction_id,subject='over')
    #                 sms.more_amount(user,code,bid.ticket_price,over)
                    
    #             else:
    #                 bid_entry = BidEntry.create(user,bid)
    #                 Transaction.record(user,amount,transaction_id,
    #                                 'bid ticket',bid_entry)
                    
    #                 sms.bid_entry_message(bid_entry)
    #                 return bid_entry
                
    #         else:

    #             sms.code_not_found(user,code)
    #             self.deposit(user,amount,transaction_id,subject='bid not found')
                
    #     else:
    #         if bid is False:
    #             sms.code_not_found(user,code)
    #             self.deposit(user,amount,transaction_id,subject='bid not found')
    #         else:
    #             sms.code_not_open(user,bid)
    #             self.deposit(user,amount,transaction_id,subject='bid not open')
            
            
    def user_exists(self,phone_number):
        return User.objects.filter(phone_number=phone_number).exists()
    
    def is_bid_id(self,code):
        
        return isinstance(code,int) and BidEntry.objects.filter(pk=code)\
            .exists()
    
    def get_bid_entry(self,code):
        
        return BidEntry.objects.get(pk=code)
    
    def create_user_bid(self,user,amount,bid_entry,source):
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
            InvalidBid.create(user,amount)
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
            if bill_ref_no.isdigit():
                amount = int(bill_ref_no)
                return {'code':None,'amount':amount,'source':'DIRECT DEPOSIT'}


            elif self.isfloat(bill_ref_no):
                amount = Decimal(bill_ref_no)
                logger.info('Amount ---{}'.format(str(amount)))
                
                return {'code':None,'amount':amount,'source':'DIRECT DEPOSIT'}

            
            else:
                
                if len(bill_ref_no.split()) == 3:
                    code = str(bill_ref_no).split()[0]
                    code = code.upper()
                    amount = str(bill_ref_no).split()[1]
                    source = str(bill_ref_no).split()[2]

                elif len(bill_ref_no.split()) == 2:
                    code = str(bill_ref_no).split()[0]
                    code = code.upper()
                    amount = str(bill_ref_no).split()[1]
                    source = 'DIRECT DEPOSIT'

                elif len(bill_ref_no.split()) == 1 and '.' not in bill_ref_no:
                    amount = bill_ref_no[3:]
                    code = bill_ref_no[0:3]
                    source = 'DIRECT DEPOSIT'



                return {'code':code,'amount':amount,'source':source}
        except Exception as e:
            user = self.get_user(phone_number)
            InvalidBid.create(user,bill_ref_no)
            DEBUG and logger.debug('TARE Error ---{}'.format(str(e)))
            return None

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
        
        
        


    








