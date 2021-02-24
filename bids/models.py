from django.db import models
from factory.models import FactoryModel
from products.models import Product
from users.models import User
from django.utils import timezone
from datetime import timedelta
from django.contrib.postgres.fields import ArrayField
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
    
    code = models.CharField(max_length=20)
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
    priority = models.IntegerField(default =0)
    closes_at = models.DateTimeField(default=timezone.now()+timedelta(weeks=1))
    lookups = ArrayField(models.CharField(max_length=100), null=True, blank=True)
    
    def __str__(self):
        return self.code

    @classmethod
    def active(cls):
        return cls.objects.filter(is_open=True).order_by('-priority')

    def cm_passed(self):
        return True if (self.entries.count()*20) >= self.critical_mass else False

    def save(self, *args, **kwargs):
        if self.critical_mass == 20.00:
            self.critical_mass = self.product.price
        super().save(*args, **kwargs)

    
    
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
                related_name='user_bids')
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    source = models.CharField(max_length=50, default='DIRECT DEPOSIT')
    non_unique_sms_sent = models.BooleanField(default=False)
    
    def __str__(self):
        return self.bid_entry.bid.code
    
    @classmethod
    def create(cls,user,bid_entry,amount,source):
        return cls.objects.create(bid_entry=bid_entry,amount=amount,source=source)

class InvalidBid(FactoryModel):

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    bid_value = models.CharField(max_length = 20,null=True,blank=True)
    notes = models.CharField(max_length=200,null=True,blank=True)
    bill_ref_no = models.CharField(max_length=20,null=True,blank=True)
    resolved = models.IntegerField(default=0)
    resolve_notes = models.CharField(max_length=200, null=True,blank=True)

    @classmethod
    def create(cls,user,bid_value,notes,bill_ref_no=bill_ref_no):
        return cls.objects.create(user= user,bid_value=bid_value,notes=notes,bill_ref_no=bill_ref_no)

    @classmethod
    def get_unprocessed(cls,limit):
        return cls.objects.filter(resolved=0).order_by('id')[:limit]



class UssdDial(FactoryModel):

    phone_number = models.CharField(max_length=13, db_index=True)
    no_of_dials = models.IntegerField(default=1)
    last_dialed = models.DateTimeField(default=timezone.now())

    @classmethod
    def create(cls,phone_number):
        defaults = {
            'phone_number':phone_number
        }
        obj,created = cls.objects.get_or_create(phone_number=phone_number,defaults=defaults)
        if not created:
            obj.no_of_dials+=1
            obj.last_dialed = timezone.now()
            obj.save()

class Advertizer(FactoryModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Survey(FactoryModel):

    phone_number = models.CharField(max_length=13, db_index=True)
    rate = models.IntegerField()
    text = models.TextField(blank=True,null=True)
    

    @classmethod
    def create(cls,phone_number,rate,text=None):
        return cls.objects.create(phone_number=phone_number,rate=rate,text=text)

class BlackList(FactoryModel):

    phone_number = models.CharField(max_length=13, db_index=True)
    bid = models.ForeignKey(Bid,on_delete=models.DO_NOTHING)
    notes = models.TextField()
    actor = models.CharField(max_length=100)

    @classmethod
    def create(cls,phone_number,bid,notes,actor):
        obj,created = cls.objects.get_or_create(phone_number=phone_number,bid=bid,
        defaults=dict(phone_number=phone_number,notes=notes,bid=bid,actor=actor))
        return obj,created
    

class Reserve(FactoryModel):
    bid = models.ForeignKey(Bid,on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=6,decimal_places=2)

    def create(cls,bid,value):
        return cls.objects.get_or_create(bid=bid,value=value,defaults=dict(bid=bid,value=value))

class ReservePass(FactoryModel):
    msisdn=models.CharField(max_length=13)
