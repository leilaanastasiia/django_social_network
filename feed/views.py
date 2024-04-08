from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views.generic import View, DetailView, UpdateView, ListView
from django_registration.backends.activation.views import RegistrationView

from djangogramm_15 import settings
from .forms import CreatePostForm, PostImageFormSet, CustomRegisterForm
from .models import Post, Profile, Photo, User, Follower, Like
from .tasks import send_register_email_async


class CustomRegistrationView(RegistrationView):
    template_name = 'feed/registration/registration_form.html'
    form_class = CustomRegisterForm
    success_url = reverse_lazy('feed:django_registration_start')
    email_body_template = 'feed/registration/activation_email_body.txt'
    email_subject_template = 'feed/registration/activation_email_subject.txt'

    def send_activation_email(self, user):
        activation_key = self.get_activation_key(user)
        context = self.get_email_context(activation_key)
        subject = render_to_string(
            template_name=self.email_subject_template,
            context=context,
            request=self.request,
        )
        # Force subject to a single line to avoid header-injection issues
        subject = ''.join(subject.splitlines())
        message = render_to_string(
            template_name=self.email_body_template,
            context=context,
            request=self.request,
        )

        # send an email with celery
        send_register_email_async.delay(user_id=user.id,
                                        subject=subject,
                                        message=message,
                                        from_email=settings.DEFAULT_FROM_EMAIL)


class IndexView(LoginRequiredMixin, View):
    login_url = 'feed:login'
    template_name = 'feed/index.html'

    def get(self, request, *args, **kwargs):
        following = Follower.objects.filter(follower=request.user).values_list('following__id')
        posts_data = Post.objects.filter(user__id__in=following)
        liked_posts = Post.objects.filter(likes__user=request.user)
        context = {
            'posts_data': posts_data,
            'liked_posts': liked_posts,
            'form': CreatePostForm(),
            'form_images': PostImageFormSet()
        }

        # ask to follow somebody
        if not posts_data:
            all_users = User.objects.exclude(username=request.user.username)
            context['all_users'] = all_users

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        post = Post.objects.create(user=request.user)
        form = CreatePostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user
            new_post.save()
            for key in form.files:
                photo_files = form.files.getlist(key)
                for file in photo_files:
                    Photo.objects.create(photo=file, user=request.user, post=new_post)
            # prevent posting an empty posts
            if not post.text and not post.photos.all().exists():
                post.delete(keep_parents=True)
            return HttpResponseRedirect('/feed/')
        else:
            form = CreatePostForm()
        return render(request, self.template_name, {"form": form})


class ProfileView(LoginRequiredMixin, DetailView):
    login_url = 'feed:login'
    model = Profile
    template_name = 'feed/profile.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.object
        context['followers_count'] = Follower.objects.filter(following=profile.user).exclude(following=profile.user).count()
        context['following_count'] = Follower.objects.filter(follower=profile.user).exclude(following=profile.user).count()
        context['is_following'] = Follower.objects.filter(follower=self.request.user, following=profile.user).exists()
        context['liked_posts'] = Post.objects.filter(likes__user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        profile = self.get_object()
        if Follower.objects.filter(follower=request.user, following=profile.user).exists():
            Follower.objects.filter(follower=request.user, following=profile.user).delete()
        else:
            Follower.objects.create(follower=request.user, following=profile.user)
        return redirect('feed:profile', profile.user.username)


class UpdateProfileView(LoginRequiredMixin, UpdateView):
    login_url = 'feed:login'
    model = Profile
    fields = ['full_name', 'avatar', 'bio']
    template_name = 'feed/profile_update.html'

    def get_success_url(self):
        return reverse_lazy('feed:profile', kwargs={'slug': self.object.slug})


class FollowersView(LoginRequiredMixin, ListView):
    login_url = 'feed:login'
    model = Follower
    template_name = 'feed/followers.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_slug = self.kwargs.get('slug')
        profile = Profile.objects.get(slug=profile_slug)
        context['profile'] = profile
        context['followers'] = Follower.objects.filter(following=profile.user).exclude(following=profile.user)
        return context


class FollowingsView(LoginRequiredMixin, ListView):
    login_url = 'feed:login'
    model = Follower
    template_name = 'feed/followings.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_slug = self.kwargs.get('slug')
        profile = Profile.objects.get(slug=profile_slug)
        context['profile'] = profile
        context['followings'] = Follower.objects.filter(follower=profile.user).exclude(following=profile.user)
        return context


class PostView(LoginRequiredMixin, DetailView):
    login_url = 'feed:login'
    model = Post
    template_name = 'feed/post.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['liked_posts'] = Post.objects.filter(likes__user=self.request.user)
        return context


@login_required
def like(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post = Post.objects.get(pk=post_id)

        if post.likes.filter(user=request.user, post=post).exists():
            post.likes.filter(user=request.user, post=post).delete()
            return JsonResponse({'unliked': True})
        else:
            post.likes.create(user=request.user, post=post)
            return JsonResponse({'liked': True})
    return HttpResponseRedirect(reverse('index'))
