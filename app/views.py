from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count
from django.db.models import F
from itertools import chain

from .models import Post, PostLike, User, Followers


@api_view(["POST"])
def create_user(request):
    """
    curl -X POST \
    --header 'Content-type: application/json' \
    --data '{
        "username": "admin",
        "password": "admin"
    }' \
    http://localhost:8000/user/create/
    """

    # Business Logic
    try:
        user = User.objects.create(
            username=request.data.get("username"), password=request.data.get("password")
        )
        user.save()
        return Response(
            {"message": "👤 inserted!"}, status=201, content_type="application/json"
        )
    except Exception:
        return Response(
            {"message": "Error occured!"}, status=500, content_type="application/json"
        )


@api_view(["POST"])
def create_post(request):
    """
    curl -X POST \
    --header 'Content-type: application/json' \
    --data '{
        "body": "This is a sample post.",
        "username": "admin"
    }' \
    http://localhost:8000/post/create/
    """

    # Business Logic
    try:
        post = Post.objects.create(
            body=request.data.get("body"),
            user=User.objects.get(username=request.data.get("username")),
        )
        post.save()
        return Response(
            {"message": "📭 inserted!"}, status=201, content_type="application/json"
        )
    except Exception:
        return Response(
            {"message": "Error occured!"}, status=500, content_type="application/json"
        )


@api_view(["POST"])
def like_post(request):
    """
    curl -X POST \
    --header 'Content-type: application/json' \
    --data '{
        "post_id": "1",
        "username": "admin1"
    }' \
    http://localhost:8000/post/like/
    """

    # Business Logic
    try:
        post = PostLike.objects.create(
            post=Post.objects.get(id=request.data.get("post_id")),
            user=User.objects.get(username=request.data.get("username")),
        )
        post.save()
        return Response(
            {"message": "👍 inserted!"}, status=201, content_type="application/json"
        )
    except Exception:
        return Response(
            {"message": "Error occured!"}, status=500, content_type="application/json"
        )


@api_view(["GET"])
def get_users(request):
    """
    curl -X GET \
    http://localhost:8000/users/top/
    """

    # Business Logic
    try:
        return Response(
            Post.objects.values(username=F("user__username"))
            .annotate(posts=Count("id"))
            .order_by(),
            status=200,
            content_type="application/json",
        )
    except Exception:
        return Response(
            {"message": "No users!"}, status=404, content_type="application/json"
        )


@api_view(["POST"])
def follow_user(request):
    """
    curl -X POST \
    --header 'Content-type: application/json' \
    --data '{
        "follower": "admin1",
        "username": "admin"
    }' \
    http://localhost:8000/users/follow/
    """
    # Business Logic
    try:
        follow_relationship = Followers.objects.create(
            user=User.objects.get(username=request.data.get("username")),
            follower=User.objects.get(username=request.data.get("follower")),
        )
        follow_relationship.save()
        return Response(
            {"message": "🏃‍♀️ Followed!"}, status=201, content_type="application/json"
        )
    except Exception:
        return Response(
            {"message": "Error occured!"}, status=500, content_type="application/json"
        )


@api_view(["GET"])
def get_user_feed(request, user_id):
    """
    curl -X GET \
    http://localhost:8000/users/feed/1/
    """
    try:
        # Business Logic
        def join_lists(post_likes, posts):
            for post in posts:
                for post_like in post_likes:
                    if post.get("id") == post_like.get("post_id"):
                        post["likes"] = post_like.get("count")

                del post["user_id"]
                del post["timestamp"]

                post["author"] = user.username

            for post in posts:
                if not "likes" in post:
                    post["likes"] = 0
            return posts

        user = User.objects.get(id=user_id)
        post_likes = PostLike.objects.values("post_id").annotate(count=Count("user_id"))
        posts = list(Post.objects.filter(user=user).values())
        posts = join_lists(post_likes, posts)

        followers = Followers.objects.filter(user=user).values("follower_id")
        follower_posts = [
            Post.objects.filter(
                user=User.objects.get(id=follower.get("follower_id"))
            ).values()
            for follower in followers
        ]
        flatten_follower_posts = list(chain.from_iterable(follower_posts))
        flatten_follower_posts = join_lists(post_likes, flatten_follower_posts)

        return Response(
            posts + flatten_follower_posts, status=200, content_type="application/json"
        )
    except Exception:
        return Response(
            {"message": "Data not found!"}, status=404, content_type="application/json"
        )
