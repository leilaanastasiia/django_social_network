from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Post, Photo, User, Profile, Follower, Like


# Register your models here.

class ProfileInLine(admin.TabularInline):
    model = Profile
    extra = 1


class PostInLine(admin.TabularInline):
    model = Post
    extra = 3


class PhotoInLine(admin.TabularInline):
    model = Photo
    extra = 3


class FollowersInLine(admin.TabularInline):
    model = Follower
    extra = 5
    fk_name = "follower"


class FollowingsInLine(admin.TabularInline):
    model = Follower
    extra = 5
    fk_name = "following"


class LikesInLine(admin.TabularInline):
    model = Like
    extra = 5


class UserAdmin(admin.ModelAdmin):
    list_display = ['username']
    inlines = [ProfileInLine, PostInLine, PhotoInLine, FollowersInLine, FollowingsInLine, LikesInLine]


admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
