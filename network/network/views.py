import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Max,Sum,Count

from .models import User, Post, Follow, Like
from .utils import is_number

def index(request):
    # Authenticated users view their inbox
    if request.user.is_authenticated:
       return render(request, "network/index.html")

    # Everyone else is prompted to sign in
    else:
        return HttpResponseRedirect(reverse("login"))

@csrf_exempt
@login_required
def new_post(request):

    # Adding a new post must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Load request body (JS puts a Json dict in it)
    data = json.loads(request.body)

    # Get contents of post
    text = data.get("text", "")

    # Save post
    post = Post(
        user=request.user,
        text=text
    )
    post.save()

    return JsonResponse({"message": "Post saved successfully."}, status=201)


@csrf_exempt
@login_required
def edit_post(request, post_id):

    # Editing a new post must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Load request body (JS puts a Json dict in it)
    data = json.loads(request.body)

    # Get contents of post
    text = data.get("text", "")

    # Edit and save post
    try:
        post = Post.objects.get(user=request.user, pk=post_id)
        post.text=text
        post.save()
        return JsonResponse({"message": "Post saved successfully."}, status=201)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found or you are not its owner."}, status=404)
    

@login_required
def view_post(request, post_id):

    posts = Post.objects.filter(pk=post_id)
    return JsonResponse([post.serialize() for post in posts], safe=False)


@login_required
def posts_list(request, list):

    # Filter posts returned based on list karg
    postInstance = Post()
    if list == "all":
        posts = postInstance.get_all()
    elif list == "by_user":
        posts = postInstance.get_own(request.user)
    elif list == "by_followed":
        posts = postInstance.get_follow(request.user)        
    else:
        return JsonResponse({"error": "Invalid request."}, status=400)

    return JsonResponse([post.serialize(request.user) for post in posts], safe=False)

@csrf_exempt
@login_required
def like(request, post_id):
    # Add or remove like
    if request.method == "PUT":
        # Load request body (JS puts a Json dict in it)
        post = Post.objects.get(pk=post_id)
        user = request.user

        data = json.loads(request.body)
        if data.get("like") is not None:
            if data["like"]:
                # Add like
                post.add_like(user)
            else:
                # Remove like
                post.remove_like(user)
            return JsonResponse({"message": "Like/unlike processed."}, status=203)
    return JsonResponse({"error": "Invalid request."}, status=400)

   
@csrf_exempt
@login_required
def follow(request):

    # Editing a follow table must be via POST
    if request.method == "PUT":        

        # Get follow's information
        data = json.loads(request.body)
        action = data.get("action", "")
        user_id = int(data.get("user", ""))

        currentUser = request.user
        followedUser = User.objects.get(pk=user_id)

        # Add/remove follows
        if action == 'follow':
            currentUser.add_follow(followedUser)
            return JsonResponse({"message": "Follow action finished successfully."}, status=201)

        if action == 'unfollow':
            request.user.remove_follow(followedUser)
            return JsonResponse({"message": "Follow action finished successfully."}, status=201)
    return JsonResponse({"error": "POST request required."}, status=400)

@login_required
def follow_list(request):
    userInstance = User()
    follow_list = userInstance.get_others(request.user)
    return JsonResponse([row.serialize(request.user) for row in follow_list], safe=False)

@login_required
def follow_counts(request):

    followed = request.user.get_followed()
    follower = request.user.get_follower()
    return JsonResponse({"followed": followed,"follower": follower }, status=201)



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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
