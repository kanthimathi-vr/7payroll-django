# accounts/decorators.py

from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def admin_required(view_func):
    """
    Decorator for views that checks if the user is logged in and has the 'ADMIN' role.
    Redirects to the dashboard if the user is not an admin.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if the user is logged in
        if not request.user.is_authenticated:
            # If not logged in, Django's @login_required (if used) handles this, 
            # but we explicitly check here for safety.
            return redirect('login') 
        
        # Check if the user is an admin (based on the CustomUser.role field)
        if request.user.role == 'ADMIN':
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Permission denied. Only Administrators can access this page.")
            return redirect('dashboard')
    return wrapper