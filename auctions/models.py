from django.contrib.auth.models import AbstractUser
from django.db import models

# user model 
class User(AbstractUser):
    pass


# bids table
class Bids(models.Model):
    bid = models.FloatField()
    total_bids = models.IntegerField(blank=True, default='0')
    current_winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="current_winner")

    def __str__(self):
        return f"bid: {self.bid}, total_bids: {self.total_bids},current_winner: {self.current_winner}"



# auction listings model 
class auction_listings(models.Model):
    # unchangable fields(fixed)
    title = models.CharField(max_length=64)
    image_url = models.URLField(blank=True) # not required (optional)
    category = models.CharField(max_length=64, blank=True) # not required (optional)
    description = models.TextField() 
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
    active = models.BooleanField(default=True)

    # changable fields
    price = models.ForeignKey(Bids, on_delete=models.CASCADE, related_name="price")

    def __str__ (self):
        return f"{self.id}, Title: {self.title}, {self.price}, image_url: {self.image_url}, category: {self.category}, description: {self.description}"



# comments table
class Comments(models.Model):
    listing = models.ForeignKey(auction_listings, on_delete=models.CASCADE, related_name="auction_listing")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"user: {self.user}, comment: {self.comment}, listing: {self.listing.id}"
