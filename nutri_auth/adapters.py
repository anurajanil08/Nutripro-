from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from .models import User

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
       
        if sociallogin.is_existing:
            return

        
        user_data = sociallogin.account.extra_data
        email = user_data.get('email')
        username = user_data.get('name') or email.split('@')[0]

        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            
            user = User.objects.create(
                email=email,
                username=username,
                is_active=True,
                is_staff=False,
                is_superuser=False,
                is_admin=False
            )
            user.save()

       
        sociallogin.connect(request, user)
