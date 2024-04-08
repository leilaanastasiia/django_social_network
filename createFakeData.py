import os
import boto3
from djangogramm_13.settings import env

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangogramm_13.settings")

import django
from django.db.models import signals

django.setup()

from random import randint
import requests
from model_bakery import baker

from feed.models import User

DOWNLOAD_AVATAR_PATH = 'feed/avatars'
DOWNLOAD_PHOTO_PATH = 'feed/profiles_photos'


def download_picsum_image(image_id, download_file_path, width, height):
    url = f"https://picsum.photos/{width}/{height}?image={image_id}"
    response = requests.get(url)

    if response.status_code == 200:
        file_name = f"{image_id}.jpg"
        s3 = boto3.resource('s3')
        file_path = f'{download_file_path}/{file_name}'
        s3_object = s3.Object(env('AWS_STORAGE_BUCKET_NAME'), file_path)
        s3_object.put(Body=response.content)
        return file_path
    return response


def main():
    signals.post_save.disconnect(sender=User, dispatch_uid="test_data")
    for amount_of_profiles in range(2):
        new_user = baker.make_recipe('feed.user')
        new_avatar = download_picsum_image(randint(1, 100), DOWNLOAD_AVATAR_PATH, width=150, height=150)
        new_profile = baker.make_recipe('feed.profile',
                                        user=new_user,
                                        avatar=new_avatar)
        for amount_of_posts in range(randint(1, 5)):
            new_post = baker.make_recipe('feed.post', user=new_profile.user)
            for amount_of_photos in range(randint(1, 3)):
                new_photo = download_picsum_image(randint(1, 100), DOWNLOAD_PHOTO_PATH, width=600, height=400)
                baker.make_recipe('feed.photo',
                                  user=new_user,
                                  post=new_post,
                                  photo=new_photo)


if __name__ == '__main__':
    main()
