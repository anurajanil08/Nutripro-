from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout

class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):      
        if request.user.is_authenticated:    
            if not request.user.is_active:
                logout(request)
                return redirect(reverse('nutri_auth:handlelogin')) 
               
        response = self.get_response(request)
        return response