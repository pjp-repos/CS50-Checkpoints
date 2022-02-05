from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User,Category,Auction, WatchList,Bid,Comment
from django.db.models import Max
from .utils import is_number,redirect_with_params

class AuctionForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all(),widget=forms.Select(attrs={'class':'form-control'}))
    #user = forms.ModelChoiceField(queryset=User.objects.all(),widget=forms.HiddenInput())
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    description = forms.CharField( widget=forms.Textarea(attrs={'class':'form-control'}))
    startBid = forms.FloatField(widget=forms.NumberInput(attrs={'class':'form-control'}))
    photo = forms.URLField( widget=forms.URLInput(attrs={'class':'form-control'}))
   




def index(request):
    return render(request, "auctions/index.html",{
        "auctions":Auction.objects.filter(status=False).annotate(maxBid = Max('bidsByAuction__bid'))
    })


def categories(request):
    return render(request, "auctions/categories.html",{
        "categories":Category.objects.all()
    })


def auctions(request,filterCriteria,filterValue):
    if filterCriteria == 'byCategory':
        # From Auction model, look at User model across Auction "category" Field to richt it (Child to father direction = direct)
        # Once there, in Category model/table, ask for description field. Add __iexact to avoid Case Sensitive action.
        auctionQs = Auction.objects.filter(category__description__iexact=filterValue,status=False).annotate(maxBid = Max('bidsByAuction__bid'))
        return  render(request, "auctions/auctions.html",{
            "auctions":auctionQs,
            "listType": f" in {filterValue} caregory"

        })
    elif filterCriteria == 'inWatchList':
        # From Auction model, look at Watchlist model across related_name "watchListAuction" (Father to child direction=reverse)
        # Once there, look at User model across Watchlist "user" Field to richt it (Child to father direction = direct)
        # Finally, once in User model/table, ask for username field.
        return  render(request, "auctions/auctions.html",{
            "auctions":Auction.objects.filter(watchListAuction__user__username=filterValue,status=False).annotate(maxBid = Max('bidsByAuction__bid')),
            "listType": f" in {filterValue} watchlist"

        })
    else:
        return HttpResponseRedirect(reverse("index"))


def create(request):
    if request.method == "POST":
        auctionForm = AuctionForm(request.POST)
        if auctionForm.is_valid():            
            row = Auction(
                        category = auctionForm.cleaned_data["category"],
                        user = request.user,
                        winnerUserName = "",
                        title = auctionForm.cleaned_data["title"],
                        description = auctionForm.cleaned_data["description"],
                        startBid = auctionForm.cleaned_data["startBid"],
                        status = False,
                        photo = auctionForm.cleaned_data["photo"]
            )
            row.save()
    
    return render(request, "auctions/create.html",{
        "auctionForm":AuctionForm()
    })


def auction(request):
    if request.method == 'GET':
        auction_id = request.GET.get('auction_id', None)
        errorBidCode = request.GET.get('errorBidCode', None)
        auctionQs = Auction.objects.filter(id=int(auction_id))
        if auctionQs.count() > 0:
            if request.user.is_authenticated:
                # Test if current listing is in the watchlist
                isInWatchlist = Auction.objects.filter(id=int(auction_id), watchListAuction__user__username=request.user.username).count()
            else:
                isInWatchlist = -1
            bidAggrgate = Bid.objects.filter(auction=Auction.objects.get(pk=int(auction_id))).aggregate(max_bid=Max('bid'))
            maxBid = bidAggrgate['max_bid']
            comments = Comment.objects.filter(auction=Auction.objects.get(pk=int(auction_id))).order_by('id').reverse()
            return render(request, "auctions/auction.html",{
                "auction":auctionQs,
                "isInWatchlist":isInWatchlist,
                "maxBid":maxBid,
                "errorBidCode":errorBidCode,
                "comments":comments
            })
    elif request.method == 'POST':
        if request.user.is_authenticated:
            # Read all post parameters
            watchlistCmd=request.POST.get("watchlistCmd", "")
            watchlistId=request.POST.get("watchlistId", "")
            bidFlag=request.POST.get("bidFlag", "")
            bidId=request.POST.get("bidId", "")
            bidValue=request.POST.get("bidValue", "")
            closeFlag=request.POST.get("closeFlag", "")
            closeId=request.POST.get("closeId", "")
            commentFlag=request.POST.get("commentFlag", "")
            commentId=request.POST.get("commentId", "")
            commentValue=request.POST.get("commentValue", "")

            # Check if POST is due to add/remove item from watchlist
            if watchlistCmd == 'add' or watchlistCmd == 'rem':
                if watchlistCmd == 'add':
                    qs = WatchList(auction=Auction.objects.get(pk=int(watchlistId)),user=request.user )
                    qs.save()
                elif watchlistCmd == 'rem':
                    WatchList.objects.filter(auction=Auction.objects.get(pk=int(watchlistId))).delete()
                return HttpResponseRedirect(reverse('auctions', kwargs={
                    'filterCriteria': 'inWatchList',
                    'filterValue': request.user.username
                }))
            # Check if POST is due to user are placing a bid
            if bidFlag == 'bid' : 
                bidAggrgate = Bid.objects.filter(auction=Auction.objects.get(pk=int(bidId))).aggregate(max_bid=Max('bid'))
                maxBid = bidAggrgate['max_bid']
                if not is_number(maxBid):
                    auctionObj = Auction.objects.get(pk=int(bidId))
                    maxBid = auctionObj.startBid
                if is_number(bidValue) :
                    if float(bidValue) > maxBid:
                        auctionObj = Auction.objects.get(pk=int(bidId))
                        auctionObj.winnerUserName = request.user.username
                        auctionObj.save()
                        qs = Bid(auction=Auction.objects.get(pk=int(bidId)),user=request.user,bid=float(bidValue) )
                        qs.save()
                        errorBidCode='0'
                    else:
                        errorBidCode='1'
                else:
                    errorBidCode='2'
                return HttpResponseRedirect(redirect_with_params('auction',auction_id=bidId,errorBidCode=errorBidCode))
            # Check if POST is due to user are sending a comment
            if commentFlag == 'comment' :  
                qs = Comment(auction=Auction.objects.get(pk=int(commentId)),user=request.user,comment=commentValue )
                qs.save()
                return HttpResponseRedirect(redirect_with_params('auction',auction_id=commentId))
            # Check if POST is due to user are closing a listing
            if closeFlag == 'close': 
                Auction.objects.filter(pk=int(closeId)).update(status=True)

    return HttpResponseRedirect(reverse('index'))


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
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
