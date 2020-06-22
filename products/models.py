from django.db import models
from factory.models import FactoryModel
from django.conf import settings

# Create your models here.
class Product(FactoryModel):
    code = models.CharField(max_length=20,unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8,decimal_places=2)
    image = models.ImageField(upload_to='products',
                              height_field='height',
                              width_field='width',max_length=500)
    width=models.CharField(max_length=20,null=True,blank=True)
    height=models.CharField(max_length=20,null=True,blank=True)
    offered = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name