from django.contrib import admin
from .models import Bid,BidEntry,UserBid,Advertizer

class BidAdmin(admin.ModelAdmin):
    list_display = ('code','critical_mass','product','ticket_price',
                    'is_open','duration','open_at','closes_at','priority','ref_no','lookups',)
    readonly_fields = ('ref_no',)
    link_display = ('code','lookups',)
    fields = ('code','critical_mass','product','ticket_price',
                    'is_open','duration','open_at','closes_at','priority','ref_no','lookups',)
    
class BidEntryAdmin(admin.ModelAdmin):
    list_display = ('user','bid')
    fields = ('user','bid')
    
class UserBidAdmin(admin.ModelAdmin):
    list_display = ('amount','bid_entry')
    fields = ('amount','bid_entry')

class AdvertizerAdmin(admin.ModelAdmin):
    list_display = ('name','created_at')
    fields = ('amount','created_at')
    
admin.site.register(Bid, BidAdmin)
admin.site.register(BidEntry, BidEntryAdmin)
admin.site.register(Advertizer, AdvertizerAdmin)

