from django.contrib.auth.models import AbstractUser
from django.template.defaultfilters import slugify
from django.db import models


class User(AbstractUser):
    username = models.CharField(max_length=25, unique=True)
    email = models.EmailField(unique=True, blank=False)

    def __str__(self):
        return f'id={self.id}, username={self.username}, email={self.email}'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(default='blank_profile_img.png', upload_to='feed/avatars')
    bio = models.TextField(max_length=300, blank=True)
    slug = models.SlugField(blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.user.username)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'id={self.id}, full_name={self.full_name}, slug={self.slug}'


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    text = models.TextField(blank=True, max_length=500)
    pub_date = models.DateTimeField('date published', auto_now_add=True)

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return f'user={self.user.username}, text={self.text[:30]}, pub_date={self.pub_date}'


class Photo(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='photos')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='feed/profiles_photos')

    def __str__(self):
        return f'photo_id={self.id}'


class Follower(models.Model):
    follower = models.ForeignKey(User, related_name="followings", on_delete=models.CASCADE, null=True)
    following = models.ForeignKey(User, related_name="followers", on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f'id={self.id}, follower={self.follower}, following={self.following}'


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f'id={self.id}, user={self.user}, post={self.post}'
