from django.db import models
from factory.models import FactoryModel


class OutgoingSMS(FactoryModel):

    phone_number=models.CharField(max_length=13)
    text=models.CharField(max_length=500)
    status=models.IntegerField(default=0)
    status_reason=models.CharField(max_length=100,blank=True,null=True)
    @classmethod
    def get_unprocessed(cls,limit):
        return cls.objects.filter(status=0).order_by('id')[:limit]

    @classmethod
    def create(cls,phone_number,text):
        return cls.objects.create(phone_number=phone_number,text=text)

