from django.contrib.auth.models import AbstractUser
from django.db import models

# user model 
class User(AbstractUser):
    pass


# bids table
class Bid(models.Model):
    bid = models.FloatField()
    winner = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"bid: {self.bid}, bidder: {self.user}, winner: {self.winner}"



# auction listings model 
class AuctionListing(models.Model):
    # unchangable fields(fixed)
    title = models.CharField(max_length=64)
    image_url = models.URLField(blank=True) # not required (optional)
    description = models.TextField() 
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    original_price = models.FloatField()

    # category
    CATEGORIES = [
        ('Cars', 'cars'),
        ('Technology', 'technology'),
        ('Education', 'education'),
        ('Home', 'home'),
        ('Art', 'art'),
        ('Gaming', 'gaming'),
        ('Toys', 'toys'),
    ]
    category = models.CharField(max_length=10, choices=CATEGORIES, blank=True) # not required (optional)

    # changable fields
    total_bids = models.IntegerField(default='0')
    active = models.BooleanField(default=True)

    price = models.ForeignKey(Bid, on_delete=models.CASCADE, blank=True)

    def __str__ (self):
        return f"{self.id}, Title: {self.title}, owner: {self.owner}, Active: {self.active}, total_bids: {self.total_bids}, {self.price}, image_url: {self.image_url}, category: {self.category}, description: {self.description}, original_price: {self.original_price}"



# comments table
class Comment(models.Model):
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()

    def __str__(self):
        return f"author: {self.author}, comment: {self.comment}, listing: {self.listing.id}"


# Watchlist table
class Watchlist(models.Model):
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")

    def __str__(self):
        return f"listing_id: {self.listing.id}, user: {self.user}"
