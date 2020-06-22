from django.urls import path
from . import views as vw

urlpatterns = [
   
    path('', vw.ProductsList.as_view()),
    path('terms/', vw.Terms.as_view()),
]