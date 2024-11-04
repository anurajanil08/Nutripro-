from django.shortcuts import redirect
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('adminpanel:adminlogin')
        if not request.user.is_admin:
            return redirect('adminpanel:adminlogin')  
        return view_func(request, *args, **kwargs)
    return _wrapped_view
