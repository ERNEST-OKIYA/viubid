from django.urls import path
from . import views as vw

urlpatterns = [
   
    path('', vw.ProductsList.as_view()),
    path('<str:code>/', vw.SpecialBid.as_view()),
    path('terms/', vw.Terms.as_view()),
    path('finished-auctions/', vw.FinishedActions.as_view()),
]
