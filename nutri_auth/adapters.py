from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from .models import User

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Check if the user already exists
        if sociallogin.is_existing:
            return

        # Get user details from sociallogin data
        user_data = sociallogin.account.extra_data
        email = user_data.get('email')
        username = user_data.get('name') or email.split('@')[0]

        # Check if a user with this email already exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Create a new user if this is the first time login
            user = User.objects.create(
                email=email,
                username=username,
                is_active=True,
                is_staff=False,
                is_superuser=False,
                is_admin=False
            )
            user.save()

        # Link the new user to the social account
        sociallogin.connect(request, user)
