import datetime
from django.db.models import signals
from django.urls import reverse
from django.test import TestCase, Client
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Post, User, Profile, Photo, Follower, Like


class GlobalSetUpTestCase(TestCase):

    def setUp(self):
        signals.post_save.disconnect(sender=User, dispatch_uid="test_data")
        self.client = Client()
        self.user = User.objects.create_user(username='alice', email='qurii@ukr,net', password='qqq')
        self.user_2 = User.objects.create(username='amanda', email='quqqrii@ukr,net', password='qqq')
        self.profile = Profile.objects.create(user=self.user, full_name='Alice Pat', bio='Sunny!')
        self.profile_2 = Profile.objects.create(user=self.user_2, full_name='Amanda Cat', bio='Cloudy!')
        self.post = Post.objects.create(user=self.user, text='Qwerty...', pub_date=timezone.now())
        self.photo = Photo.objects.create(post=self.post, user=self.user, photo=SimpleUploadedFile(
            name='test_image.jpg', content=b"some content"))
        self.follower = Follower.objects.create(follower=self.user, following=self.user_2)
        self.like = Like.objects.create(user=self.user_2, post=self.post)
        self.client.login(username='alice', password='qqq')


class ModelsTest(GlobalSetUpTestCase):

    def test_create_data(self):
        """
        Creating model's data test
        """
        self.assertEqual(str(self.user),
                         f'id={self.user.id}, username={self.user.username}, email={self.user.email}')
        self.assertEqual(str(self.user_2),
                         f'id={self.user_2.id}, username={self.user_2.username}, email={self.user_2.email}')
        self.assertEqual(str(self.profile),
                         f'id={self.profile.id}, full_name={self.profile.full_name}, slug={self.profile.slug}')
        self.assertEqual(str(self.profile_2),
                         f'id={self.profile_2.id}, full_name={self.profile_2.full_name}, slug={self.profile_2.slug}')
        self.assertEqual(str(self.post),
                         f'user={self.post.user.username}, text={self.post.text[:30]}, pub_date={self.post.pub_date}')
        self.assertEqual(str(self.photo),
                         f'photo_id={self.photo.id}')
        self.assertEqual(str(self.follower),
                         f'id={self.follower.id}, follower={self.user}, following={self.user_2}')
        self.assertEqual(str(self.like),
                         f'id={self.like.id}, user={self.user_2}, post={self.post}')


class IndexViewTests(GlobalSetUpTestCase):

    def test_index_get_method(self):
        response = self.client.get(reverse('feed:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feed/index.html')
        self.assertIn('posts_data', response.context)
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.profile.slug)

    def test_no_posts_get_method(self):
        """
        An empty posts list`s test
        """
        Post.objects.all().delete()
        response = self.client.get(reverse('feed:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No posts yet.')

    def test_post_valid_form(self):
        response = self.client.post(reverse('feed:index'), {
            'text': 'Test post text',
            'photos-0-photo': open('feed/static/feed/images/favicon.png', 'rb')
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful post
        self.assertTrue(Post.objects.filter(user=self.user, text='Test post text').exists())

    def test_post_empty_form(self):
        response = self.client.post(reverse('feed:index'), {
            'text': '',
            'photos-0-photo': ''
        })
        self.assertRedirects(response, reverse('feed:index'))  # Form should be shown again
        self.assertFalse(Post.objects.filter(user=self.user, text='').exists())

    def test_post_only_text_form(self):
        response = self.client.post(reverse('feed:index'), {
            'text': 'Test post text',
            # Missing required 'photos-0-photo' field
        })
        self.assertRedirects(response, reverse('feed:index'))
        self.assertTrue(Post.objects.filter(user=self.user, text='Test post text').exists())


class ProfileViewTest(GlobalSetUpTestCase):

    def test_profile(self):
        url = reverse('feed:profile', args=(self.profile.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.profile.bio)

    def test_profile_update(self):
        response = self.client.post(reverse('feed:profile_update',  args=(self.profile.slug,)), {
            'full_name': 'Alice Nonaht',
            'avatar': open('feed/static/feed/images/favicon.png', 'rb'),
            'bio': 'Empty sentence....'
        })
        self.assertRedirects(response, reverse('feed:profile', args=(self.profile.slug,)))
        self.assertTrue(Profile.objects.filter(user=self.user, full_name='Alice Nonaht').exists())


class PostViewTest(GlobalSetUpTestCase):

    def test_get_post(self):
        post = self.post
        url = reverse('feed:post', args=(self.post.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, post.text)


class FollowersViewTest(GlobalSetUpTestCase):

    def test_get_followers(self):
        url = reverse('feed:followers', args=(self.profile.slug,))
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'feed/followers.html')
        self.assertEqual(response.status_code, 200)
        self.assertIn('followers', response.context)


class FollowingsViewTest(GlobalSetUpTestCase):

    def test_get_followers(self):
        url = reverse('feed:followings', args=(self.profile.slug,))
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'feed/followings.html')
        self.assertEqual(response.status_code, 200)
        self.assertIn('followings', response.context)


class LikeViewTest(GlobalSetUpTestCase):

    def test_like_post(self):
        response = self.client.post(reverse('feed:like'), {
            'post_id': self.post.id,
        })
        self.assertTrue(Like.objects.filter(user=self.user, post=self.post.id).exists())
