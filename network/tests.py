from django.test import TestCase
from django.utils.timezone import now

from .models import User, Post, Follow

# Create your tests here.
class PostTestCase(TestCase):

    def setUp(self):

        # create posts
        p1 = Post.objects.create(poster=1, post_content="test case post #1", datetime=now)
        p2 = Post.objects.create(poster=2, post_content="test case post #2", datetime=now, likes=3)
        p3 = Post.objects.create(poster=3, post_content="test case post #3", datetime=now, likes=5)

        # create follows
        f1 = Follow.objects.create(user_id=1, following_user_id=2)
        f2 = Follow.objects.create(user_id=3, following_user_id=3)

    # test number of posts
    def test_posts_count(self):
        p = Post.objects.all()
        self.assertEqual(p.count(), 3)
