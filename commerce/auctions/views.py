import re
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
import json
from .models import AuctionList, Category, User, Bid

def index(request):
    user = request.user
    global contador
    contador = 0
    if user.is_authenticated:
        if user.watchlist == "":
            list = []
            contador = 0 
        else:
            list = json.loads(user.watchlist)
            contador = len(list) 
        return render(request, "auctions/index.html", {
           "auctions": AuctionList.objects.filter(active=True),
           "contador": contador
        })
    else:
        return render(request, "auctions/index.html", {
           "auctions": AuctionList.objects.filter(active=True),
           "contador": 0
        })

def my_listings(request):
    user = request.user
    if user.is_authenticated:
        list = json.loads(user.watchlist)
        contador = len(list) 
        return render(request, "auctions/index.html", {
           "auctions": AuctionList.objects.filter(user=user),
           "contador": contador
        })
    else:
        return render(request, "auctions/index.html", {
           "auctions": AuctionList.objects.filter(active=True),
           "contador": 0
        })

def all_listings(request):
    user = request.user
    if user.is_authenticated:
        list = json.loads(user.watchlist)
        contador = len(list) 
        return render(request, "auctions/index.html", {
           "auctions": AuctionList.objects.all(),
           "contador": contador
        })
    else:
        return render(request, "auctions/index.html", {
           "auctions": AuctionList.objects.all(),
           "contador": 0
        })

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


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


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
        if user.watchlist == "":
            user.watchlist = "[]"
        user.save()
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def new_auction(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
        url_image = request.POST["image"]
        auction = AuctionList()
        category_id = request.POST["categories"]
        auction.category = Category.objects.get(id=category_id) 
        auction.active = True
        auction.title = title
        auction.description = description
        auction.price = starting_bid
        auction.url_image = url_image
        userid = request.POST["userid"]
        user_object = User.objects.get(id=userid)
        auction.user = user_object
        auction.save()
        return HttpResponseRedirect(reverse("index"))

    else:
        user = request.user
        if user.watchlist == "":
            list = []
            contador = 0 
        else:
            list = json.loads(user.watchlist)
            contador = len(list) 
        return render(request, "auctions/new_auction.html", {
            "contador": contador,
            "categories":Category.objects.all()
        })

def listing(request, id): 
    user = request.user
    if user.watchlist == "":
        user.watchlist = "[]"
    user.save()
    global message_bid 
    message_bid = None
    auction = AuctionList.objects.get(id=id)
    category = auction.category
    if category is None:
        category = "No category Listed"
    else:
        category = auction.category.name
    if len(auction.url_image) == 0:
        withimg = False
    else:
        withimg = True
    list = json.loads(user.watchlist)
    contador = len(list)
    if request.method == "GET":
        bids = Bid.objects.filter(auction=auction)
        bids_total = len(bids)
        amount = None
        max = 0
        for bid in bids:
            if bid.amount > max:
                max = bid.amount
            if bid.user == user:
                amount = bid.amount
        if request.user == auction.user:
            current_bid_message = f"The highest bidder belongs to {auction.user.username} "
        else:
            if max == amount:
                current_bid_message = "Your bid is the current bid."
            else:
                current_bid_message = "Your bid is not the current bid."

        message_final = f"{bids_total} bid(s) so far. {current_bid_message} "
        if auction.active == False and request.user!= bid.winner:
            message_final = "Auction closed"
        if auction.active == False and request.user == bid.winner:
            message_final = "Auction closed. You are the winner"
        in_watchlist = False
        if auction.id in list:
            in_watchlist = True
        return render(request, "auctions/listing.html", {
            "listing": auction,
            "listedby": auction.user.username,
            "withimg": withimg,
            "contador": contador,
            "category": category,
            "bids_total": bids_total, 
            "amount": auction.price,
            "message": message_bid,
            "bids_message": message_final,
            "active": auction.active,
            "in_watchlist": in_watchlist
        })
    elif request.method == "POST":
        bids = Bid.objects.filter(auction=auction)
        bids_total = len(bids)
        amount = None
        max = 0
        for bid in bids:
            if bid.amount > max:
                max = bid.amount
            if bid.user == user:
                amount = bid.amount
        if max == amount:
            current_bid_message = "Your bid is the current bid."
        else: 
            current_bid_message = "Your bid is not the current bid."
        if float(request.POST["placebid"]) <= auction.price: 
            message_bid = "Bid must be bigger than actual bid"
            return render(request, "auctions/listing.html", {
                "listing": auction,
                "listedby": auction.user.username,
                "withimg": withimg,
                "contador": contador,
                "category": category,
                "bids_total": bids_total, 
                "amount": float(request.POST["placebid"]),
                "message": message_bid,
                "bids_message": f"{bids_total} bid(s) so far. {current_bid_message}",
                "active": auction.active
            })
        if amount is None:
            bid = Bid()
        else:
            bids = Bid.objects.filter(auction=auction, user=user)
            bid = bids[0] 
        auction.price = float(request.POST["placebid"])
        auction.save()
        bid.amount = float(request.POST["placebid"])
        bid.user = user
        bid.auction = auction
        bid.save()

        current_bid_message = "Your bid is the current bid."
        return render(request, "auctions/listing.html", {
            "listing": auction,
            "listedby": auction.user.username,
            "withimg": withimg,
            "contador": contador,
            "category": category,
            "bids_total": len(Bid.objects.filter(auction=auction)), 
            "amount": auction.price,
            "message": message_bid,
            "bids_message": f"{len(Bid.objects.filter(auction=auction))} bid(s) so far. {current_bid_message}",
        })

def add_to_watchlist(request, id):
    user = request.user
    list = json.loads(user.watchlist)
    if id in list :
        list.remove(id)
    else:
        list.append(id)


    user.watchlist = json.dumps(list)
    user.save()
    return HttpResponseRedirect(reverse("listing", args=[id]))


def watchlist(request):
    user = request.user
    ids = json.loads(user.watchlist)
    watchlist = []
    for id in ids:
        watchlist.append(AuctionList.objects.get(id=id))
    contador = len(watchlist)
    return render(request, "auctions/index.html", {
        "auctions": watchlist,
        "contador": contador
    })

def categories(request):
    user = request.user
    list = json.loads(user.watchlist)
    contador = len(list)
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories,
        "contador" : contador,
    })

def category(request, id):
    user = request.user
    auctions = AuctionList.objects.filter(category=id)
    list = json.loads(user.watchlist)
    contador = len(list)

    return render(request, "auctions/index.html", {
        "auctions": auctions,
        "contador": contador,
    })

def edit_auction(request,id):
    user = request.user
    article = AuctionList.objects.get(id=id)
    category = article.category
    if category is None:
        category = "No category Listed"
    else:
        category = article.category.name
    
    if request.method == "POST":
        article.title = request.POST["title"]
        category_id = request.POST["categories"]
        article.category = Category.objects.get(id=category_id) 
        if "active" in request.POST:
            article.active = True
        else:
            article.active = False
        article.description = request.POST["description"]
        article.price = request.POST["starting_bid"]
        article.url_image = request.POST["image"]
        userid = request.POST["userid"]
        user_object = User.objects.get(id=userid)
        article.user = user_object
        article.save()
        return HttpResponseRedirect(reverse("index"))

    else:
        list = json.loads(user.watchlist)
        contador = len(list)
        return render(request, "auctions/edit_auction.html", {
            "contador": contador,
            "listing": article,
            "categories": Category.objects.all(),
        })

def close_auction(request,id):
    article = AuctionList.objects.get(id=id)
    if request.method == "POST":
        if "active" in request.POST:
            article.active = False
            article.save()
        bids = Bid.objects.filter(auction=article)
        max = 0
        winner = None
        for bid in bids:
            if bid.amount > max:
                max = bid.amount
                bid.winner = bid.user
                bid.save()
        return HttpResponseRedirect(reverse("index"))
