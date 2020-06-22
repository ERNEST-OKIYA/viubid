from django.contrib.auth.models import BaseUserManager

from django.contrib.auth.base_user import BaseUserManager
from messaging.models import OutgoingSMS


class UserManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, phone_number, password, **extra_fields):
        #do validations

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        message = "Welcome to CHOMOA HELA - Game Rahisi washindi Kibao.Tuma 20/= kwa Paybill 523388 Kisha Bonyeza *680# na unaeza shinda 20,000/= au Jackpot Mzuka PAPO HAPO!"
        OutgoingSMS.create(phone_number,message)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(phone_number, password, **extra_fields)
