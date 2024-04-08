from django.conf.urls.static import static
from django.shortcuts import redirect
from django.urls import path, reverse_lazy
from django.contrib.auth import views as django_views
from django.views.generic import TemplateView

from django_registration.backends.activation.views import ActivationView

from djangogramm_15 import settings
from . import views
from .forms import CustomPasswordResetForm

app_name = 'feed'

urlpatterns = [
    # FEED
    path('feed/', views.IndexView.as_view(), name='index'),
    path('', lambda request: redirect('feed/', permanent=False)),
    path('feed/<int:pk>/', views.PostView.as_view(), name='post'),  # ex: feed/5/
    path('feed/like/', views.like, name='like'),
    path('feed/profile/<slug:slug>/', views.ProfileView.as_view(), name='profile'),  # ex: feed/profile/alice
    path('feed/profile/<slug:slug>/followers', views.FollowersView.as_view(), name='followers'),
    path('feed/profile/<slug:slug>/followings', views.FollowingsView.as_view(), name='followings'),
    path('feed/profile/update/<slug:slug>/', views.UpdateProfileView.as_view(),
        name='profile_update'),

    # REGISTRATION
    path('registration/', views.CustomRegistrationView.as_view(),
        name='django_registration_register'),
    # an activation email has been sent
    path('registration/start', TemplateView.as_view(
        template_name="feed/registration/registration_start.html"),
        name='django_registration_start'),
    path('activate/complete/', TemplateView.as_view(
        template_name="feed/registration/activation_complete.html"),
        name="django_registration_activation_complete"),
    # have to be after activate/complete/ to load success_url
    path('activate/<str:activation_key>/', ActivationView.as_view(
        template_name='feed/registration/activation_failed.html',
        success_url=reverse_lazy('feed:django_registration_activation_complete')),
        name="django_registration_activate"),

    # LOGIN
    path('login/', django_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', django_views.LogoutView.as_view(next_page='feed:login'), name='logout'),

    # PASSWORD RESET
    # ask an email
    path('password_reset/', django_views.PasswordResetView.as_view(
        template_name='feed/registration/password_reset.html',
        form_class=CustomPasswordResetForm,
        html_email_template_name='feed/registration/password_reset_email.html',
        success_url=reverse_lazy('feed:password_reset_done')),
        name='password_reset'),
    # send an email
    path('password_reset/done/', django_views.PasswordResetDoneView.as_view(
        template_name='feed/registration/password_reset_done.html'), name='password_reset_done'),
    # link from the email
    path('password_reset_confirm/<uidb64>/<token>/', django_views.PasswordResetConfirmView.as_view(
        template_name='feed/registration/password_reset_confirm.html',
        success_url=reverse_lazy('feed:password_reset_complete')),
        name='password_reset_confirm'),
    # password accepted
    path('password-reset-complete/', django_views.PasswordResetCompleteView.as_view(
        template_name='feed/registration/password_reset_complete.html'),
        name='password_reset_complete'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
