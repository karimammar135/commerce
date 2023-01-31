from django.contrib import admin
from .models import auction_listings, User, Bids

# Register your models here.
admin.site.register(auction_listings)
admin.site.register(User)
admin.site.register(Bids)