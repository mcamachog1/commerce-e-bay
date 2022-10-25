from django.contrib import admin
from .models import AuctionList, Bid, Category, User, Comment

# Register your models here.
admin.site.register(AuctionList)
admin.site.register(Bid)
admin.site.register(User)
admin.site.register(Comment)
admin.site.register(Category)
# Register your models here.
