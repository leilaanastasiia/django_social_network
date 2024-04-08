from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.forms import ModelForm, Textarea
from django.forms.models import inlineformset_factory
from django_registration.forms import RegistrationForm

from feed.models import Post, User, Profile, Photo
from feed.tasks import send_reset_email_async, send_register_email_async


class CustomRegisterForm(RegistrationForm):

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(max_length=254, widget=forms.TextInput())

    def send_mail(self, subject_template_name, email_template_name, context,
                  from_email, to_email, html_email_template_name=None):
        context['user'] = context['user'].id

        send_reset_email_async.delay(subject_template_name=subject_template_name,
                                     email_template_name=email_template_name,
                                     context=context, from_email=from_email, to_email=to_email,
                                     html_email_template_name=html_email_template_name)


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class PhotoForm(ModelForm):
    photo = MultipleFileField()

    class Meta:
        model = Photo
        fields = ['photo', ]
        labels = {'photo': "Upload some pics"}


class CreatePostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', ]
        widgets = {
            'text': Textarea(attrs={
                'cols': 50,
                'rows': 3,
            }),
        }
        labels = {'text': "What's on your mind?"}


PostImageFormSet = inlineformset_factory(Post, Photo, form=PhotoForm, fk_name='post', extra=1, can_delete=False)
