"""QuickBid URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from products import views as vw
from admin_portal.views import *
from django.contrib.auth import views as auth_views
from admin_portal.views import ExportDialsCsv, ExportPlayersCsv,ExportInvalidCsv

urlpatterns = [
    path('', vw.ProductsList.as_view()),
    path('ussd', include('ussd.urls')),
    path('terms/', vw.Terms.as_view()),
    path('faq/', vw.Faqs.as_view()),
    path('grappelli/', include('grappelli.urls')),
    path('totals/', totals, name='totals'),
    path('ipn/', include('payments.urls')),
    path('mgr/', include('admin_portal.urls')),
    path('admin/', admin.site.urls),
    path('process_payins/', process_payins, name='process_payins'),
    path('process_bids/', process_bids, name='process_bids'),
    path('ussd-dials/', process_dials, name='process_dials'),
    path('process-active-bids/', process_active_bids, name='process-active-bids'),
    path('process-all-bids/', process_all_bids, name='process-all-bids'),
    path('process_winners/', process_winners, name='process_winners'),
    path('process_players/', process_players, name='process_players'),
    path('process_products/', process_products, name='process_products'),
    path('process-invalid/', process_invalid, name='process_invalid'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('export-bidders/',ExportPlayersCsv.as_view() , name='export-bidders'),
    path('export-winners/',ExportWinnersCsv.as_view() , name='export-winners'),
    path('export-dials/',ExportDialsCsv.as_view() , name='export-dials'),
    path('export-invalid/',ExportInvalidCsv.as_view() , name='export-invalid'),

    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'),name='login'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Text to put at the end of each page's < title > .
admin.site.site_title = 'QuickBid Admin'

# Text to put in each page's <h1> (and above login form).
admin.site.site_header = 'QuickBid Admin'

# Text to put at the top of the admin index page.
admin.site.index_title = 'QuickBid  Administration Portal'

