from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    # user
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
    # post_content
    post_content = models.CharField(max_length=280)
    # date / time of post
    datetime = models.DateTimeField(default=now)
    # users who like the post
    likers = models.ManyToManyField(User, blank=True, related_name="liked_posts")
    # number of likes
    likes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.poster}: {self.post_content}"

class Follow(models.Model):
    # follower
    user_id = models.ForeignKey(User, related_name="following", on_delete=models.CASCADE)
    # person being followed
    following_user_id = models.ForeignKey(User, related_name="followers", on_delete=models.CASCADE)

    # ensures there can only be instance of each user following another particular user
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'following_user_id'], name="Unique_follow")
        ]

    def __str__(self):
        return f"{self.user_id} is following {self.following_user_id}."
