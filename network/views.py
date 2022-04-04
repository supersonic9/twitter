from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
import json

from .models import User, Post, Follow


def index(request):
    # query to get posts, chronologically ordered, add pagination handling
    posts = Post.objects.all().order_by('-datetime')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == "POST":
        # variables to save in Post database
        post_content = request.POST["new_post"]
        poster = request.user
        # create Post object to save new post into database
        p = Post(poster=poster, post_content=post_content)
        p.save()
        # return to index page
        return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "network/index.html", {
            "page_obj": page_obj
        })


def edit(request):
    # ensure request method is POST
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        # get data from AJAX post request
        data_all = json.loads(request.body)
        # create variables for the post and id data from the request
        updated_post = data_all['updated_content']
        post_id = data_all['post_id']
        # access post that user is editing
        edited_post = Post.objects.get(id=post_id)
        # update post_content attribute of that post
        edited_post.post_content = updated_post
        # save edited post
        edited_post.save()
        # dictionary to send back to template to load asyncronously without refreshing page
        data = {
            "post_content": edited_post.post_content
        }
        # use JsonResponse to turn above dict into JSON object, send back to template
        return JsonResponse(data, status=200)
    # return error if not post request
    else:
        return HttpResponse("Error - not a post request.")


def following(request):
        # get user_id's of those the user follows using reverse relationship ('following')
        following = request.user.following.all().values_list('following_user_id', flat=True)
        # retrieve posts by those the user follows using poster__in
        posts_by_those_following = Post.objects.filter(poster__in = list(following)).order_by('-datetime')
        # add pagination handling
        paginator = Paginator(posts_by_those_following, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, "network/following.html", {
            "page_obj": page_obj
        })


def like(request):
    # ensure method is post
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        # get data from AJAX post request
        data_all = json.loads(request.body)
        # create variable for post_id
        post_id = data_all['liked_post_id']
        # access post the user is liking
        post = Post.objects.get(id=post_id)
        # update likers and likes attributes of that post
        post.likers.add(request.user)
        post.likes += 1
        post.save()
        # make dict to send back to template to update asyncronously without refresh
        data = {
            "likes": post.likes
        }
        # return data to template via JSON Response (which turns data dict into a JSON object)
        return JsonResponse(data, status=200)
    # return error message if not a post request
    else:
        return HttpResponse("Error - not a valid path without a post request")


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


def profile(request, profile_id):
    # set variables to pass to render
    already_following = False
    is_not_self = True

    # check is profile is users own
    if profile_id == request.user.id:
        is_not_self = False

    # get profile to pass to render
    profile = User.objects.get(id=profile_id)
    # get profiles posts to pass to render
    users_posts = Post.objects.filter(poster=profile).order_by('-datetime')

    # add pagination handling
    paginator = Paginator(users_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # check if user already follows this profile, update variable passed to render if so
    relationship = Follow.objects.filter(user_id=request.user.id, following_user_id=profile.id)
    if len(relationship) > 0:
        already_following = True

    # get number of followers of this profile to pass to render
    followers = len(profile.followers.all())
    # get number of profiles this profile is following to pass to render
    following = len(profile.following.all())

    if request.method == "POST":
        # update database to create a follow entry if user submitted follow
        if "follow" in request.POST:
            Follow.objects.create(user_id=request.user, following_user_id=profile)
            return HttpResponseRedirect(reverse("profile", args=(profile.id,)))

        # update database to remove a follow entry if user submitted unfollow
        if "unfollow" in request.POST:
            # use relationship variable from above to delete
            relationship.delete()
            return HttpResponseRedirect(reverse("profile", args=(profile.id,)))

    else:
        return render(request, "network/profile.html", {
            "already_following": already_following,
            "followers": followers,
            "following": following,
            "is_not_self": is_not_self,
            "profile": profile,
            "page_obj": page_obj,
    })


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


def unlike(request):
    # ensure method is post
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        # get data from AJAX post request
        data_all = json.loads(request.body)
        # create variable for post_id
        post_id = data_all['unliked_post_id']
        # access post the user is unliking
        post = Post.objects.get(id=post_id)
        # remove M2M relationship of user liking this post via related field ('liked_posts')
        delete_like_of_post = request.user.liked_posts.get(id=post_id)
        delete_like_of_post.delete()
        # update likes attributes of that post
        post.likes -= 1
        post.save()
        # make dict to send back to template to update asyncronously without refresh
        data = {
            "likes": post.likes
        }
        # return data to template via JSON Response (which turns data dict into a JSON object)
        return JsonResponse(data, status=200)
    # return error message if not a post request
    else:
        return HttpResponse("Error - not a valid path without post request.")
