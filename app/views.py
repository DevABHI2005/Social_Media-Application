from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount# Comment
# from .forms import CommentForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import uuid
from itertools import chain
import random
from django.core.files.storage import default_storage

# Create your views here.

@login_required(login_url='/signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))

    # user suggestion starts
    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)
    
    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if ( x not in list(current_user))]
    random.shuffle(final_suggestions_list)

    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))


    return render(request, 'index.html', {'user_profile': user_profile, 'posts':feed_list, 'suggestions_username_profile_list': suggestions_username_profile_list[:4]})




# def post_list(request):
#     posts = Post.objects.all()
#     if request.method == 'POST':
#         form = CommentForm(request.POST)
#         if form.is_valid():
#             comment = form.save(commit=False)
#             comment.user = request.user
#             comment.post = get_object_or_404(Post, id=request.POST.get('post_id'))
#             comment.save()
#             return redirect('post_list')  # Replace with the name of your view or URL name
#     else:
#         form = CommentForm()
#     return render(request, 'post_list.html', {'posts': posts, 'form': form})

@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user = user, caption = caption, image = image)
        new_post.save()

        return redirect('/')
    else:
        return redirect('/')

@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)
        
        username_profile_list = list(chain(*username_profile_list))
    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})

@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    # Check if the user has already liked the post
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    # Validate the post_id
    # if not post_id:
    #     return JsonResponse({'error': 'Post ID is required'}, status=400)
    
    # try:
    #     # Validate if post_id is a valid UUID (if your Post model uses UUIDs)
    #     post_id = uuid.UUID(post_id)
    # except ValueError:
    #     return JsonResponse({'error': 'Invalid Post ID format'}, status=400)

    # # Get the post or return a 404 if it doesn't exist
    # post = get_object_or_404(Post, id=post_id)

    # # Check if the user has already liked the post
    # like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter is None:
        # Add a new like
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.likes += 1
        post.save()
        return redirect('/')
        # return JsonResponse({'message': 'Post liked successfully', 'likes': post.likes}, status=200)
    else:
        # Remove the existing like
        like_filter.delete()
        post.likes -= 1
        post.save()
        return redirect('/')
        # return JsonResponse({'message': 'Post unliked successfully', 'likes': post.likes}, status=200)

@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user = user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user = user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    user_followers = len(FollowersCount.objects.filter(user = pk))
    user_following = len(FollowersCount.objects.filter(follower = pk))
    

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'profile.html', context)

@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower,user = user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/' +user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/' +user)

    else:
        return redirect('/')


@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user = request.user)
    if request.method == 'POST':

        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']
            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        return redirect('settings')
    return render(request, 'settings.html', {'user_profile': user_profile})

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Validate password and confirmation password
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("signup")  # Return a redirect

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("signup")  # Return a redirect
        
        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect("signup")

        # Create the user if validation passes
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        user_login = auth.authenticate(username = username, password = password)
        auth.login(request, user_login)

        # Create the profile for the new user
        user_model = User.objects.get(username=username)  # Fetch the user object
        new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
        new_profile.save()

        # Add success message
        messages.success(request, "Account created successfully!")
        return redirect("settings")  # Redirect to login after successful signup

    # For GET request, render the signup form
    return render(request, "signup.html")

def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username = username, password = password)

        if user is not None:
            auth.login(request, user)
            return redirect("index")
        else:
            messages.info(request, "Invalid username or password")
            return redirect("signin")
    else:
        return render(request, "signin.html")


@login_required(login_url = 'signin')
def logout(request):

    auth.logout(request)
    return redirect('signin')



from django.core.files.storage import default_storage

