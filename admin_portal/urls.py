
from django.conf.urls import url

from .views import *

urlpatterns=[

            url('^dashboard/$', Dashboard.as_view(), name='dashboard'),
            url('^$', Dashboard.as_view(), name='dashboard'),
            # # url('', Dashboard.as_view(), name='dashboard'),
            url('^winners/$', Winners.as_view(), name='winners'),
            url('^sms-outbox/$', OutBox.as_view(), name='outbox'),
            url('^bids/$', Bids.as_view(), name='bids'),
            url('^ussd-dials/$', UssdDials.as_view(), name='ussd-dials'),
            url('^products/$', Products.as_view(), name='products'),
            url('^active-bids/$', ActiveBids.as_view(), name='active-bids'),
            url('^bid-actions/$', BidActions.as_view(), name='bid-actions'),
            url('^all-bids/$', AllBids.as_view(), name='all-bids'),
            url('^bidders/$', Players.as_view(), name='bidders'),
            url('^payins/$', IncomingPayments.as_view(), name='payins'),
            url('^invalid-bids/$', InvalidBids.as_view(), name='invalid-bids'),
            


            ]
