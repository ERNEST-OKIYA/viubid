
from django.conf.urls import url
from .views import KenyaSafaricomUssdView, GhanaMtnUssdView


urlpatterns=[
	url(r'^$', KenyaSafaricomUssdView.as_view(), name='ke_saf_ussd'),
	url(r'^gh/mtn/$', GhanaMtnUssdView.as_view(), name='gh_mtn_ussd'),
]