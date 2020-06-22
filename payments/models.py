from django.db import models
from factory.models import FactoryModel
from users.models import User
import uuid
from django.db.models import Avg, Count, Min, Sum

# Create your models here.

class PayIn(FactoryModel):

    transaction_id = models.CharField(max_length=20,unique=True)
    transaction_time = models.CharField(max_length=50)
    transaction_amount = models.DecimalField(max_digits=8,decimal_places=2)
    bill_reference_number = models.CharField(max_length=50,null=True,blank=True)
    org_account_balance = models.CharField(max_length=50)
    msisdn = models.CharField(max_length=16)
    first_name = models.CharField(max_length=50,null=True,blank=True)
    middle_name = models.CharField(max_length=50,null=True,blank=True)
    last_name = models.CharField(max_length=50,null=True,blank=True)
    status = models.IntegerField(default=0)
    status_reason = models.CharField(max_length=200,blank=True, null=True)


    @classmethod
    def create(cls,transaction_id,transaction_time,\
        transaction_amount,bill_reference_number,\
            org_account_balance,msisdn,first_name,middle_name,last_name):
        return cls.objects.create(transaction_id=transaction_id,\
            transaction_time=transaction_time,\
                transaction_amount=transaction_amount,\
                    bill_reference_number=bill_reference_number,\
                        org_account_balance=org_account_balance,msisdn=msisdn,\
                            first_name=first_name,middle_name=middle_name,
                            last_name=last_name)

    @classmethod
    def get_unprocessed(cls,limit):
        return cls.objects.filter(status=0).order_by('id')[:limit]

    @classmethod
    def get_total_deposits(cls):
       return cls.objects.aggregate(
		Sum('transaction_amount'))['transaction_amount__sum']





class CheckoutResponse(FactoryModel):
    response = models.TextField()
    status = models.IntegerField(default=0)
    status_reason = models.CharField(max_length=200)

    @classmethod
    def get_unprocessed(cls,limit):
        return cls.objects.filter(status=0).order_by('id')[:limit]

class RawCheckout(FactoryModel):
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    reference_number = models.CharField(max_length=20)
    amount = models.IntegerField()
    status = models.IntegerField(default=0)
    status_reason = models.CharField(max_length=200)

    @classmethod
    def create(cls,user,amount):
        return cls.objects.create(user=user,amount=amount)


    @classmethod
    def get_unprocessed(cls,limit):
        return cls.objects.filter(status=0).order_by('id')[:limit]






