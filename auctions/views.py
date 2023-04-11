from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, AuctionListing, Bid, Comment, Watchlist

from django.contrib import messages #import messages

from datetime import datetime

# returning index(main) page
def index(request):

    # get only the first four listings
    all_listings = AuctionListing.objects.all()
    listings = []
    count = 0
    for listing in all_listings:
        count += 1
        if count > 4:
            exit
        else:
            listings.append(listing)

    return render(request, "auctions/index.html", {
        "listings": listings
    })

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

        # if there is no provided image assign it with the default image
        if image_url == "":
            image_url = "https://us.123rf.com/450wm/yehorlisnyi/yehorlisnyi2104/yehorlisnyi210400016/167492439-no-photo-or-blank-image-icon-loading-images-or-missing-image-mark-image-not-available-or-image.jpg?ver=6"

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
        "active_listings": AuctionListing.objects.all(),
        "footer": "explore_categories"
    })


## displaying listings in watchlist to the user 
@login_required
def watchlist(request):

    # getting all listings in the watchlist
    current_user = request.user
    watchlist = current_user.watchlist.all()
    listings = []
    for listing in watchlist:
        listings.append(listing.listing)

    # checking if the watchlist is empty
    if listings == []:
        footer = "empty_watchlist"
    else: 
        footer = "none"

    # display all the data in the database related to the auction listing to the user
    return render(request, "auctions/active_listings.html", {
        "active_listings": listings,
        "footer": footer
    })


## error page 
def error(request):
    return render(request, "auctions/error.html")


## show details about a listing to the user 
@login_required
def listing_details(request, id):
    
    ## if bids form submitted using post method
    if request.POST.get("form_name") == "bid":

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
            # redirect the user to the page that displays all active listings 
            return render(request, "auctions/error.html", {
                "error": "Your bid was not submitted successfuly. You have to provide a larger bid."
            })


    ## if comments form submitted using post method
    elif request.POST.get("form_name") == "comment":

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
        return HttpResponseRedirect(reverse("listing_details", args=(listing.id,)))
    


    ## delete a comment
    elif request.POST.get("form_name") == "delete_comment":

        # get comment id
        comment_id = request.POST["comment_id"]

        # get the specific comment from the database
        comment = Comment.objects.get(id=comment_id)

        # delete the comment 
        comment.delete()

        # redirect the user to a page that displays all active listings 
        listing = AuctionListing.objects.get(id = id)
        return HttpResponseRedirect(reverse("listing_details", args=(listing.id,)))



    ## if close auction form submitted using post method
    elif request.POST.get("form_name") == "close_auction":
        
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
        
        # redirect the user to a page that displays all active listings 
        return HttpResponseRedirect(reverse("watchlist"))


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
        return HttpResponseRedirect(reverse("watchlist"))



    # if get method 
    else:
        # get the specific auction listing and the comments made on it
        listing = AuctionListing.objects.get(id = id)
        comments = listing.comments.all()
        
        # calculate the time between the date of creation and the current date of the comments
        comments_times = {}
        for comment in comments:
            # creation date
            creation_date = str(comment.created_on)[:10]

            # current date
            current_date = str(datetime.now())[:10]

            # convert the d\string dates into date objects
            d1 = datetime.strptime(creation_date, "%Y-%m-%d")
            d2 = datetime.strptime(current_date, "%Y-%m-%d")

            # difference between the two dates in timedelta
            delta = d2 - d1
            comment_time = ""
           
            # possible time values
            if delta.days == 0:
                comment_time = "just now"
            elif (delta.days/30) > 1:
                if int(delta.days/30) > 12:
                    if int((int(delta.days)/30)/12) == 1:
                        comment_time = "1 year ago"
                    else:
                        comment_time = f"{int((int(delta.days)/30)/12)} years ago"
                else:
                    comment_time = f"{int(delta.days/30)} month ago"
            elif delta.days == 1:
                comment_time = f"{delta.days} day ago"
            else: 
                comment_time = f"{delta.days} days ago"
            
            # add the comment time to the dictionary
            comments_times.update({comment.id: comment_time})
        
        
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
            "comments_times": comments_times,
            "total_comments": total_comments,
            "current_user": current_user,
            "watchlist": watchlist
        })



# available categories and there required data
cars = [
    'Cars',
    'https://researchleap.com/wp-content/uploads/2015/12/5.-luxury-cars-in-china.jpg',
]
technology = [
    'Technology',
    'https://www.deccanherald.com/sites/dh/files/styles/article_detail/public/articleimages/2023/01/23/scienceistock-1183792-1674473443.jpg?itok=bc45v91O',
]
education = [
    'Education',
    'https://media.istockphoto.com/id/1320882544/photo/glowing-light-bulb-and-book-or-text-book-with-futuristic-icon-self-learning-or-education.jpg?s=612x612&w=0&k=20&c=1fCGnLilpVhM1rw2DKgtTcujYezmelfPFYPB4dyhuuk=',
]
home = [
    'Home',
    'https://cdn.homedit.com/wp-content/uploads/2011/02/decorate-the-bookshelf-with-diff-books.jpg',
]
art = [
    'Art',
    'https://imgv3.fotor.com/images/slider-image/goart_guide_pc_now_3.jpg',
]
gaming = [
    'Gaming',
    'https://www.reviewgeek.com/p/uploads/2020/12/19a62eff.jpg?height=200p&trim=2,2,2,2',
]
toys = [
    'Toys',
    'https://rare-gallery.com/uploads/posts/4577090-indiana-jones-lego-motorcycle-water.jpg',
]

## listing categories
def categories(request):

    # categories
    categories = [
        cars,
        technology,
        education,
        home,
        art,
        gaming,
        toys,
    ]

    return render(request, "auctions/categories.html", {
        "categories": categories
    })



## displaying category's listings
def category_listings(request, category_name):

    # categories
    categories = {
        "Cars": cars,
        "Technology": technology,
        "Education": education,
        "Home": home,
        "Art": art,
        "Gaming": gaming,
        "Toys": toys,
    }

    # getting the category's image
    category = categories[category_name]
    category_img = category[1]
    
    # get listings present in the specific category
    all_listings = AuctionListing.objects.filter(category=category_name)
    
    items = 0
    listings = []
    for original_listing in all_listings:
        listing = [
            items%2,
            original_listing
        ]
        listings.append(listing)
        items += 1
        
    if items == 0:
        listings = ""

    # render an html page showing all listings in the category
    return render(request, "auctions/category_listings.html", {
        "category_name": category_name,
        "category_img": category_img,
        "listings": listings
    })