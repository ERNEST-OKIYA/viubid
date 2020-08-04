from django.db import models
from factory.models import FactoryModel
from users.models import User
from bids.models import Bid

# Create your models here.
class Winner(FactoryModel):

    user = models.ForeignKey(User, on_delete = models.DO_NOTHING)
    bid = models.ForeignKey(Bid, on_delete = models.DO_NOTHING)
    winning_value = models.DecimalField(max_digits=10, decimal_places=2)

    @classmethod
    def create(cls,user,bid,winning_value):
        return cls.objects.create(user=user,bid=bid,winning_value=winning_value)
    
