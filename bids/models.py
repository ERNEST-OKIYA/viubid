from django.db import models
from factory.models import FactoryModel
from products.models import Product
from users.models import User
from django.utils import timezone
from datetime import timedelta
# Create your models here.


import random
import string


def generate_ref_no(sl=5):
    letters = string.ascii_uppercase
    return ''.join(random.choice(letters) for i in range(sl))
class BidDuration:
    ONE_HOUR = 'ONE_HOUR'
    ONE_WEEK = 'ONE WEEK'
    ONE_MONTH = 'ONE MONTH'
    
    BID_DURATION_CHOICES = [
    (ONE_HOUR, 'ONE HOUR'),
    (ONE_WEEK, 'ONE WEEK'),
    (ONE_MONTH, 'ONE MONTH'),

    ]
    
class Bid(FactoryModel):
    
    code = models.CharField(max_length=20,unique=True)
    ref_no = models.CharField(max_length = 5,default = generate_ref_no)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING,
                                related_name='product')
    critical_mass = models.DecimalField(max_digits=8,decimal_places=2,default = 20.00)
    ticket_price = models.DecimalField(max_digits=8,decimal_places=2,default=20.00)
    
    is_open = models.BooleanField(default=False)
    is_critical_mass_passed = models.BooleanField(default=False)
    duration = models.CharField(max_length=20,
        choices=BidDuration.BID_DURATION_CHOICES,
        default=BidDuration.ONE_WEEK)
    open_at = models.DateTimeField(default=timezone.now)
    closes_at = models.DateTimeField(default=timezone.now()+timedelta(weeks=1))
    
    def __str__(self):
        return self.code
    
class BidEntry(FactoryModel):
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    bid = models.ForeignKey(Bid,on_delete=models.DO_NOTHING,
                        related_name='entries')
    
    
    def __str__(self):
        return self.bid.code
    
    # def save(self, *args, **kwargs):
    #     if self.pk:
    #         if (self.pk.count()*self.bid.ticket_price)>=self.bid.critical_mass:
    #             self.bid.is_open = True
    #             self.is_critical_mass_passed = True
    #             self.bid.open_at = timezone.now()
    #             self.bid.save()
    #     super().save(*args, **kwargs)
    
    
    @classmethod
    def create(cls,user,bid):
        return cls.objects.create(user=user,bid=bid)
    
class UserBid(FactoryModel):
    bid_entry = models.ForeignKey(BidEntry,on_delete=models.DO_NOTHING,
                related_name='bid_entries')
    amount = models.DecimalField(max_digits=8,decimal_places=2)
    source = models.CharField(max_length=50, default='DIRECT DEPOSIT')
    non_unique_sms_sent = models.BooleanField(default=False)
    
    def __str__(self):
        return self.bid_entry.bid.code
    
    @classmethod
    def create(cls,user,bid_entry,amount,source):
        return cls.objects.create(bid_entry=bid_entry,amount=amount,source=source)

class InvalidBid(FactoryModel):

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    bid_value = models.CharField(max_length = 20)

    @classmethod
    def create(cls,user,bid_value):
        return cls.objects.create(user= user,bid_value=bid_value)



class UssdDial(FactoryModel):

    phone_number = models.CharField(max_length=13, db_index=True)
    no_of_dials = models.IntegerField(default=0)
    last_dialed = models.DateTimeField(default=timezone.now())

    @classmethod
    def create(cls,phone_number):
        if cls.objects.filter(phone_number=phone_number).exists():
            obj = cls.objects.get(phone_number=phone_number)
            obj.no_of_dials+=1
            obj.last_dialed = timezone.now()
            obj.save()
        else:
            cls.objects.create(phone_number=phone_number)