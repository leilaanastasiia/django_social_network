# Djangogramm
___

Instagram-like web application for posting images and thoughts, searching for friends, and much more!

Stack: `Django`, `PostgreSQL`, `Nginx`, `Gunicorn`, `Celery`, `Bootstrap`, `Amazon Web Services`, `pytest`

Features:
- Registration via email, Google or GitHub
- Password reset with an email confirmation (celery)
- After registration full access to the profile is granted (bio, avatar, and full name can be changed)
- Posting photos and text
- Follow/unfollow other users 
- Like/unlike posts (ajax)
- Feed with posts from followed users 

Covered with pytest. 

Was developed to be hosted at AWS (EC2, RDS, S3) on a Linux instance with Gunicorn and nginx.

All needed environmental variables can be checked in djangogramm_15/.env.example file. 




