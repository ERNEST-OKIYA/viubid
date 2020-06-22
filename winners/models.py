from django.db import models
from factory.models import FactoryModel
from users.models import User
from bids.models import Bid

# Create your models here.
class Winner(FactoryModel):

    user = models.ForeignKey(User, on_delete = models.DO_NOTHING)
    bid = models.ForeignKey(Bid, on_delete = models.DO_NOTHING)
    
