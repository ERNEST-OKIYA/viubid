from django.db import models
from factory.models import FactoryModel
from users.models import User
from django.utils import timezone

# Create your models here.







class Transaction(FactoryModel):
     user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
     amount = models.IntegerField()
     transaction_id = models.CharField(max_length=200)
     transaction_type = models.CharField(max_length=50)
     subject = models.CharField(max_length=100,null=True,blank=True)
  


     @classmethod
     def record(cls,user,amount,transaction_id,transaction_type,subject=None):
         subject = None or subject
         return cls.objects.create(user=user,amount=amount,\
         transaction_id=transaction_id,transaction_type=transaction_type,
         subject=subject)





class Wallet(FactoryModel):

    def three_day_hence():
        return timezone.now() + timezone.timedelta(days=7)


    user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    balance = models.IntegerField(default=0)
    bonus = models.IntegerField(default=0)
    is_bonus_active = models.BooleanField(default=False)
    # is_sms_sent = models.IntegerField(default=0)
    bonus_expiry = models.DateTimeField(default=three_day_hence)

    @classmethod
    def create(cls,user):
        return cls.objects.create(user=user)

    @classmethod
    def credit(cls,user,amount):
        wallet = cls.objects.get(user=user)
        wallet.balance += amount
        return wallet.save()

    @classmethod
    def debit(cls, user, amount):
        wallet = cls.objects.get(user=user)
        wallet.balance -= amount
        return wallet.save()

    @classmethod
    def credit_bonus(cls, user, amount):
        wallet = cls.objects.get(user=user)
        wallet.bonus += amount
        return wallet.save()

    @classmethod
    def debit_bonus(cls, user, amount):
        wallet = cls.objects.get(user=user)
        wallet.bonus -= amount
        return wallet.save()

    @classmethod
    def bonus_balance(cls,user):
        if cls.objects.get(user=user).is_bonus_active == False:
            return 0
        return cls.objects.get(user=user).bonus

    @classmethod
    def wallet_balance(cls, user):
        return cls.objects.get(user=user).balance

    @classmethod
    def reset_bonus(cls, user):
        w = cls.objects.get(user=user)
        w.bonus=0
        w.save()

    @classmethod
    def reset_balance(cls, user):
        w = cls.objects.get(user=user)
        w.balance=0
        w.save()


    @classmethod
    def get_uprocessed_bonus(cls,limit):
        return cls.objects.filter(bonus__gt=0).\
            filter(is_bonus_active=False).order_by('id')[:limit]

    

