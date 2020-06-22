from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .models import Product
from bids.models import Bid
from django.views import View

# Create your views here.
class ProductsList(View):
    def get(self,request):
        
        bids = Bid.objects.filter(is_open=True).all()
        next_bids = Bid.objects.filter(product__offered=True).order_by('-id')[1:5]
        # products = {
        #     'name':bid.product.name,
        #     'price':bid.product.price,
        #     'description':bid.product.description,
        #     'code': bid.product.code,
        #     'image':bid.product.image.url,
            # 'n_name':next_bids.product.name,
            # 'n_price':next_bids.product.price,
            # 'n_description':next_bids.product.description,
            # 'n_code':next_bids.product.code,
            # 'n_image':next_bids.product.image.url,
            
        


        return render(request,'products/bid.html',{'bids':bids,'next_bids':next_bids})
    
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
