from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import (
    PermissionsMixin, AbstractBaseUser
)
from django.contrib.auth.models import Permission, Group

from django.utils import timezone
from django.conf import settings
from .managers import UserManager
from factory.models import FactoryModel
from simple_history.models import HistoricalRecords
# Create your models here.


class User(AbstractBaseUser, PermissionsMixin):


    phone_number = models.CharField(max_length=16, unique=True)
    password = models.CharField(max_length=300)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(
        default=False,
        help_text='Designates whether the user can log into this admin site.'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this user should be treated as active. '
    )
    created_by = models.CharField(max_length=50, null=True)
    is_password_changed = models.BooleanField(default=False)
    is_bonus_awarded = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)
    date_created = models.DateTimeField("Date Joined", auto_now_add=True)
    objects = UserManager()
    # is_sms_sent = models.IntegerField(default =0)
    history = HistoricalRecords()

    USERNAME_FIELD = 'phone_number'

    def __str__(self):
        return self.phone_number

    def permissions(self):
        #return permsisions in the groups that the user is in
        return [p.codename for p in Permission.objects.filter(group__user=self)]

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

     def get_full_name(self):
        return self.profile.first_name + ' ' + self.profile.last_name


    
class Profile(FactoryModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,related_name='profile')
    first_name = models.CharField(max_length=50,blank=True,null=True)
    middle_name = models.CharField(max_length=50, blank=True,null=True)
    last_name = models.CharField(max_length=50,blank=True, null=True)

    @classmethod
    def create(cls,user,first_name,middle_name,last_name):
        defaults = {
                    'first_name':first_name,
                    'middle_name':middle_name,
                    'last_name':last_name
                   }
        return cls.objects.update_or_create(user=user,defaults=defaults)

