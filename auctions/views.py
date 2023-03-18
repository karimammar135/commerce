from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, AuctionListing, Bid, Comment, Watchlist

from django.contrib import messages #import messages

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
            owner = request.user

            # make a starting bid and save it to the database
            bid = Bid(bid=starting_bid, user=owner, winner=True)
            bid.save()

            # save the data in the sqlite database 
            new_listing = AuctionListing(title=title, price=bid, original_price=starting_bid, image_url=image_url, category=category, description=description, owner=owner)
            new_listing.save()

            # redirect the user to a page that displays all active listings 
            return HttpResponseRedirect(reverse("active_listings"))
        

    # if get request
    else:
        return render(request, "auctions/create_listing.html")


## displaying active listings to the user 
@login_required
def active_listings(request):

    # display all the data in the database related to the auction listing to the user
    return render(request, "auctions/active_listings.html", {
        "active_listings": AuctionListing.objects.all()
    })


## error page 
def error(request):
    return render(request, "auctions/error.html")


## show details about a listing to the user 
@login_required
def listing_details(request, id):
    
    ## if bids form submitted using post method
    if request.POST.get("form_name") == "bid":
        print("bid form")

        # collecting submitted data
        if request.POST["bid"] == "":
            return render(request, "auctions/error.html", {
                "error": "Provide a bid."
            })
        else:
            new_bid = float(request.POST["bid"])

        # current logged in user
        current_user = request.user

        # getting the auction listing according to it's id
        listing = AuctionListing.objects.get(id = id)

        # verify if the auction is active or not
        if listing.active == False:
            # redirect the user to a page that displays all active listings 
            return HttpResponseRedirect(reverse('listing_details', kwargs={'id':id}))

        # save the data in the database(bids' table) if the new bid is greater than the old one
        if new_bid > listing.price.bid:

            # make the last bid not a winner (winner=flase)
            listing.price.winner = False
            listing.price.save()

            # make a new bid and save it to the database
            bid = Bid(bid=new_bid, user=current_user, winner=True)
            bid.save()

            # save the bid in the auction_listings model
            listing.price = bid
            listing.price.save()

            # modefy total bids
            listing.total_bids += 1
            listing.save()
            
            print(f"{listing}")
            
            # redirect the user to a page that displays all active listings 
            return HttpResponseRedirect(reverse("active_listings"))
            
        else:
            print("you have to give a larger bid")
            # redirect the user to the page that displays all active listings 
            return render(request, "auctions/error.html", {
                "error": "Your bid was not submitted successfuly. You have to provide a larger bid."
            })


    ## if comments form submitted using post method
    elif request.POST.get("form_name") == "comment":
        print("comment form")

        # collecting submitted data
        comment = str(request.POST["add_comment"])

        # current logged in user
        current_user = request.user

        # getting the auction listing according to it's id
        listing = AuctionListing.objects.get(id = id)

        # add the data to the database(comments' table)
        comment = Comment(listing=listing, comment=comment, author=current_user)
        comment.save()

        # redirect the user to a page that displays all active listings 
        return HttpResponseRedirect(reverse("active_listings"))
    



    ## if close auction form submitted using post method
    elif request.POST.get("form_name") == "close_auction":
        print("auction closed")
        
        # getting the auction listing according to it's id
        listing = AuctionListing.objects.get(id = id)

        # change the value of active in the database to false in order to close the auction
        listing.active = False
        listing.save()

        # redirect the user to a page that displays all active listings 
        return HttpResponseRedirect(reverse("active_listings"))



    ## if add to watchlist form submitted using post method
    elif request.POST.get("form_name") == "add_watchlist":

        # taking listing id from the form 
        listing_id = request.POST["listing_id"]
        
        # taking the listing from the database
        listing = AuctionListing.objects.get(id=listing_id)

        # current logged in user
        current_user = request.user

        # create the watchlist object
        watchlist = Watchlist(listing=listing, user=current_user)
        watchlist.save()
        
        print(f"added to watchlist {watchlist}")
        
        # redirect the user to a page that displays all active listings 
        return HttpResponseRedirect(reverse("active_listings"))


    ## if remove from watchlist form submitted using post method
    elif request.POST.get("form_name") == "remove_watchlist":
        # get listing id from the form 
        listing_id = request.POST["listing_id"]
        
        # get the listing from the database
        listing = AuctionListing.objects.get(id=listing_id)

        # current logged in user
        current_user = request.user

        # get the specific watchlist object and delete it
        watchlist = Watchlist.objects.get(listing=listing, user=current_user)
        watchlist.delete()

        # redirect the user to a page that displays all active listings 
        return HttpResponseRedirect(reverse("active_listings"))



    # if get method 
    else:
        # get the specific auction listing and the comments made on it
        listing = AuctionListing.objects.get(id = id)
        comments = listing.comments.all()

        # calculating the number of comments comments
        total_comments = 0
        for comment in comments:
            total_comments += 1

        # checking if the listing is active
        active = listing.active
        
        # get the current user of the listing
        current_user = request.user

        # checking if the listing is added to the watchlist
        try:
            watchlist = current_user.watchlist.get(listing=listing)
            watchlist = True
        except:
            watchlist = False
        
        # desplaying an html page with all the details of an auction listing
        return render(request, "auctions/listing_details.html", {
            "listing": listing,
            "comments": comments,
            "total_comments": total_comments,
            "current_user": current_user,
            "watchlist": watchlist
        })
