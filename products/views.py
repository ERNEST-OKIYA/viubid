from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .models import Product
from bids.models import Bid
from django.views import View

# Create your views here.
class ProductsList(View):
    def get(self,request):
        
        bids = Bid.objects.filter(is_open=True).all().order_by('-priority')
        next_bids = Bid.objects.filter(product__offered=True).order_by('-id')[1:5]
        previous_bids = Bid.objects.filter(is_open=False).all()
        return render(request,'products/bid.html',{'bids':bids,'previous_bids':previous_bids})
    
    def post(self,request):
        pass
    
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

class Terms(View):

    def get(self,request):
        return render(request,'products/terms.html')

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

class Faqs(View):

    def get(self,request):
        return render(request,'products/faq.html')

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
