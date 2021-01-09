from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .models import Product
from bids.models import Bid
from winners.models import Winner
from django.views import View


# Create your views here.
class ProductsList(View):
    def get(self,request):
        
        bids = Bid.objects.filter(is_open=True).all().order_by('-priority')
        winners = Winner.objects.all().order_by('-id')[:4]
        return render(request,'products/index.html',{'bids':bids,'winners':winners})
        
    
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

class SpecialBid(View):
    
    def get(self,request): 
        bids = Bid.objects.filter(id=3).all()
        winners = Winner.objects.all().order_by('-id')
        return render(request,'products/special-bid.html',{'bids':bids,'winners':winners})
    
    def post(self,request):
        pass
    
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

