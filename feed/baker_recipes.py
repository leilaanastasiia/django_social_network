from faker import Faker
from model_bakery.recipe import Recipe, related, foreign_key

from feed.models import User, Profile, Post, Photo

fake = Faker()


user = Recipe(
    User,
    username=fake.unique.user_name,
    email=fake.email,
)

profile = Recipe(
    Profile,
    user=foreign_key(user),
    full_name=fake.name,
    avatar=fake.image_url(placeholder_url='https://picsum.photos/150/150'),
    bio=fake.paragraph,
)

post = Recipe(
    Post,
    user=related(user),
    text=fake.sentence
)

photo = Recipe(
    Photo,
    user=related(user),
    post=related(post),
    photo=fake.image_url(placeholder_url='https://picsum.photos/600/300')
)