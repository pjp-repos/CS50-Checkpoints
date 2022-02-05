from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import CharField


class User(AbstractUser):
    pass


class Category(models.Model):
    description = models.CharField(max_length=32, unique=True)
    def __str__(self):
        return f"{self.description}"


class Auction(models.Model):
    category = models.ForeignKey(Category,on_delete=CASCADE, related_name="byCategory")
    user = models.ForeignKey(User,on_delete=CASCADE, related_name="byUser")
    winnerUserName = models.CharField(max_length=32,null=True,blank=True)
    title = models.CharField(max_length=32)
    description = models.TextField()
    startBid = models.FloatField()
    status = models.BooleanField()
    photo = models.URLField(blank=True)
    def __str__(self):
        return f"{self.title} in {self.category.description} category, created by {self.user.username}"


class Bid(models.Model):
    auction = models.ForeignKey(Auction,on_delete=CASCADE, related_name="bidsByAuction")   
    user = models.ForeignKey(User,on_delete=CASCADE, related_name="bidsByUser")
    bid = models.FloatField()
    def __str__(self):
        return f"Auction title: {self.auction.title}, amount:  {self.bid}. Bid user: {self.user.username}"

class Comment(models.Model):
    auction = models.ForeignKey(Auction,on_delete=CASCADE, related_name="commentsByAuction")   
    user = models.ForeignKey(User,on_delete=CASCADE, related_name="commentsByUser")
    comment = models.CharField(max_length=128)
    def __str__(self):
        return f"Auction title: {self.auction.title}, comment:  {self.comment}. Comment user: {self.user.username}"

class WatchList(models.Model):
    auction = models.ForeignKey(Auction,on_delete=CASCADE,related_name="watchListAuction")   
    user = models.ForeignKey(User,on_delete=CASCADE,related_name="watchListUser")
    def __str__(self):
        return f"Auction title: {self.auction.title}, in watchlist of: {self.user.username}"