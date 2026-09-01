from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from posts.models import Post, Tag, Like, Comment, Bookmark, Story
from accounts.models import Profile, Follow
from django.core.files.uploadedfile import SimpleUploadedFile


class PainaimaTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username="testuser1", password="password123")
        self.user2 = User.objects.create_user(username="testuser2", password="password123")
        
        # Test image (1x1 transparent gif)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        self.uploaded_image = SimpleUploadedFile("test.gif", small_gif, content_type="image/gif")
        
        self.post = Post.objects.create(
            author=self.user1,
            caption="Hello world! Check this #sunset #cafe @testuser2",
            location="Bangkok",
            image=self.uploaded_image,
        )

    def test_feed_view_anonymous_redirects_to_login(self):
        """Anonymous users must be redirected to login page."""
        res = self.client.get(reverse("core:feed"))
        self.assertEqual(res.status_code, 302)
        self.assertIn(reverse("account_login"), res.url)

    def test_feed_view_authenticated(self):
        self.client.login(username="testuser1", password="password123")
        res = self.client.get(reverse("core:feed"))
        self.assertEqual(res.status_code, 200)

    def test_explore_view_and_search(self):
        self.client.login(username="testuser1", password="password123")
        res = self.client.get(reverse("core:explore"))
        self.assertEqual(res.status_code, 200)

        # Search by tag
        res_tag = self.client.get(reverse("core:explore") + "?q=%23sunset")
        self.assertEqual(res_tag.status_code, 200)
        self.assertContains(res_tag, "sunset")

    def test_search_api(self):
        self.client.login(username="testuser1", password="password123")
        res = self.client.get(reverse("core:search_api") + "?q=test")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("users", data)

    def test_post_detail(self):
        res = self.client.get(reverse("posts:post_detail", kwargs={"pk": self.post.pk}))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Hello world!")

    def test_like_toggle_ajax(self):
        self.client.login(username="testuser2", password="password123")
        res = self.client.post(reverse("posts:like_toggle", kwargs={"pk": self.post.pk}))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["liked"])
        self.assertEqual(data["likes_count"], 1)

        # Unlike
        res2 = self.client.post(reverse("posts:like_toggle", kwargs={"pk": self.post.pk}))
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertFalse(data2["liked"])
        self.assertEqual(data2["likes_count"], 0)

    def test_comment_ajax(self):
        self.client.login(username="testuser2", password="password123")
        res = self.client.post(
            reverse("posts:add_comment", kwargs={"pk": self.post.pk}),
            {"text": "Cool post!", "is_ajax": "1"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(self.post.comments.count(), 1)

    def test_follow_toggle(self):
        self.client.login(username="testuser2", password="password123")
        res = self.client.post(reverse("accounts:toggle_follow", kwargs={"username": "testuser1"}))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["is_following"])
        self.assertTrue(Follow.objects.filter(follower=self.user2, following=self.user1).exists())

    def test_profile_view(self):
        self.client.login(username="testuser1", password="password123")
        res = self.client.get(reverse("accounts:profile", kwargs={"username": "testuser1"}))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "testuser1")

    def test_share_to_story(self):
        self.client.login(username="testuser2", password="password123")
        res = self.client.post(reverse("posts:share_to_story", kwargs={"pk": self.post.pk}))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertTrue(Story.objects.filter(user=self.user2, shared_post=self.post).exists())

    def test_story_create_view(self):
        self.client.login(username="testuser1", password="password123")
        res = self.client.post(
            reverse("posts:story_create"),
            {"media_file": self.uploaded_image, "caption": "Awesome day!", "is_ajax": "1"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["story"]["caption"], "Awesome day!")

    def test_story_like_toggle(self):
        self.client.login(username="testuser1", password="password123")
        story = Story.objects.create(user=self.user1, media_file=self.uploaded_image, caption="Like me")
        res = self.client.post(reverse("posts:story_like_toggle", kwargs={"story_id": story.id}))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["liked"])
        self.assertEqual(data["likes_count"], 1)

    def test_story_reply_api(self):
        self.client.login(username="testuser2", password="password123")
        story = Story.objects.create(user=self.user1, media_file=self.uploaded_image, caption="My story")
        res = self.client.post(
            reverse("posts:story_reply_api", kwargs={"story_id": story.id}),
            {"text": "So lovely!"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(story.replies.count(), 1)

    def test_get_stories_api(self):
        self.client.login(username="testuser1", password="password123")
        Story.objects.create(user=self.user1, media_file=self.uploaded_image, caption="My daily vibe")
        res = self.client.get(reverse("posts:get_user_stories_api", kwargs={"username": "testuser1"}))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["stories"]), 1)
