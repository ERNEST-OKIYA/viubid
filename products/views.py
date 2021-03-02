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
        return render(request,'products/newterms.html')

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

class Faqs(View):

    def get(self,request):
        return render(request,'products/faqs.html')

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

class SpecialBid(View):
    
    def get(self,request,code): 
        bids = Bid.objects.filter(code__icontains=code,is_open=True).all()
        bid = Bid.objects.filter(code__icontains=code).last()
        name = bid.product.name
        code = bid.code
        winners = Winner.objects.all().order_by('-id')
        return render(request,'products/special-bid.html',{'bids':bids,'winners':winners,'name':name,'code':code})
    
    def post(self,request):
        pass
    
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

class FinishedActions(View):
    def get(self,request): 
        winners = Winner.objects.all().order_by('-id')
        return render(request,'products/completed-auctions.html',{'winners':winners})
    
    def post(self,request):
        pass
    
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


