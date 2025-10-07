from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test

def admin_required(function=None, redirect_field_name=None, login_url='/accounts/login/'):
    """
    Decorator for views that checks that the user is logged in AND is an ADMIN,
    redirecting to the login page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.role == 'ADMIN',
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator