from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, auction_listings, Bids

# returning index(main) page
def index(request):
    return render(request, "auctions/index.html")

# login 
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


#logout 
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


# register for new account
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


# create a new listing 
@login_required
def create_listing(request):
    # if post request
    if request.method == "POST":

        # collecting data from the user
        title = request.POST["title"]
        image_url = request.POST["image_url"]
        category = request.POST["category"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]

        # checking for errors
        if title == "" or description == "" or starting_bid == "":
            return HttpResponseRedirect(reverse("error"))

        # if there was no errors
        else:
            # current logged in user
            current_user = request.user

            # saving data related to the bids models
            bid = Bids(bid=starting_bid, current_winner=current_user)
            bid.save()

            # save the data in the sqlite database 
            new_listing = auction_listings(title=title, price=bid, image_url=image_url, category=category, description=description, owner=current_user)
            new_listing.save()

            # redirect the user to a page that displays all active listings 
            return HttpResponseRedirect(reverse("active_listings"))
        

    # if get request
    else:
        return render(request, "auctions/create_listing.html")


## displaying active listings to the user 
def active_listings(request):

    # display all the data in the database related to the auction listing to the user
    return render(request, "auctions/active_listings.html", {
        "active_listings": auction_listings.objects.all()
    })


## error page 
def error(request):
    return render(request, "auctions/error.html")
