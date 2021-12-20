
from django.conf.urls import url
from django.urls import path

from .views import *

urlpatterns=[

            url('^incoming/$', Payins.as_view(), name='payins'),
            url('^validate/$', ValidatePayins.as_view(), name='validate-payins'),
            url('^checkout-response/$', CheckoutResult.as_view(), name='checkout_response'),
            url('^checkout/$', Checkouts.as_view(), name='checkout'),
            path('stk-push-create/<str:msisdn>/<int:bid_value>/<str:bid_code>/', mediapal_push,name='stkpush_create'),



            ]
