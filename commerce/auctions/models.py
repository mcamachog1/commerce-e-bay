from django.contrib.auth.models import AbstractUser
from django.db import models
import json



class User(AbstractUser):
    pass
    watchlist = models.TextField(blank = True)

class Category(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    def __str__(self):
        return f"{self.id}: {self.name} - {self.description}"

class AuctionList(models.Model):
    active = models.BooleanField()
    title = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    url_image = models.CharField(max_length=200, blank = True)
    description = models.TextField(blank = True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listing")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="categories", null=True)

    def __str__(self):
        return f"{self.id}: {self.title} - {self.description}"

class Bid(models.Model):
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    auction = models.ForeignKey(AuctionList, on_delete=models.CASCADE, related_name="user_offers")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="offers")
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="winner", null = True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}: {self.user.username} - {self.amount} - {self.auction.title}" 

class Comment(models.Model):
    auction = models.ForeignKey(AuctionList, on_delete=models.CASCADE, related_name="user_comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}: {self.user.username} : {self.comment}" 