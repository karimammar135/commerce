from django.contrib.auth.models import AbstractUser
from django.db import models

# user model 
class User(AbstractUser):
    pass


# bids table
class Bids(models.Model):
    bid = models.FloatField()
    current_winner = models.CharField(max_length=64)

    def __str__(self):
        return f"bid: {self.bid}, current_winner: {self.current_winner}"


# auction listings model 
class auction_listings(models.Model):
    # unchangable fields(fixed)
    title = models.CharField(max_length=64)
    image_url = models.URLField(blank=True) # not required (optional)
    category = models.CharField(max_length=64, blank=True) # not required (optional)
    description = models.TextField() 
    owner = models.CharField(max_length=64, blank=True)
    active = models.BooleanField(default=True)

    # changable fields
    price = models.ForeignKey(Bids, on_delete=models.CASCADE, related_name="price")

    def __str__ (self):
        return f"{self.id}, Title: {self.title}, {self.price}, image_url: {self.image_url}, category: {self.category}, description: {self.description}"

