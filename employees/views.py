from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction

# Import our custom models, forms, and decorator
from employees.models import EmployeeProfile
from employees.forms import EmployeeUserForm, EmployeeProfileForm
from accounts.decorators import admin_required 
from accounts.models import CustomUser

# C:\vetri\finalbackendprojects\7employee_payroll\employees\views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
# Import other models/data needed for the dashboard here

@login_required # Best practice: ensure only logged-in users can access the dashboard
def dashboard_view(request):
    """
    Renders the main employee dashboard.
    """
    
    # Check if the user has an employee profile (to prevent the previous error)
    # This is a critical check for your payroll system
    try:
        profile = request.user.employeeprofile
    except AttributeError:
        # If the profile doesn't exist, redirect them to a setup page or show an error
        # For now, let's render a simple error page or redirect to admin
        return redirect('admin:index') 

    context = {
        'title': 'Employee Dashboard',
        'user_profile': profile,
        # Add any other data needed for the dashboard (e.g., latest payslip, remaining leave)
    }

    # IMPORTANT: You must create this dashboard.html template!
    return render(request, 'employees/dashboard.html', context)



# 1. READ (List All Employees)
@login_required
@admin_required # Only Admins can see the list
def employee_list(request):
    employees = EmployeeProfile.objects.filter(user__is_active=True).select_related('user')
    context = {'employees': employees, 'title': 'Employee Directory'}
    return render(request, 'employees/employee_list.html', context)


# 2. CREATE (Add New Employee)
@login_required
@admin_required
@transaction.atomic # Ensures both User and Profile are saved, or neither is.
def employee_create(request):
    if request.method == 'POST':
        user_form = EmployeeUserForm(request.POST)
        profile_form = EmployeeProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            # 1. Save the CustomUser
            new_user = user_form.save(commit=False)
            new_user.set_password(request.POST.get('password')) # Set and hash password
            
            # Ensure role is set to EMPLOYEE if not explicitly chosen otherwise
            if not new_user.role:
                new_user.role = 'EMPLOYEE'

            new_user.save()

            # 2. Save the EmployeeProfile, linking it to the new user
            new_profile = profile_form.save(commit=False)
            new_profile.user = new_user
            new_profile.save()

            messages.success(request, f"Employee {new_user.get_full_name()} added successfully!")
            return redirect('employee_list')
        
        else:
            # Handle form errors
            pass

    else: # GET request
        user_form = EmployeeUserForm()
        profile_form = EmployeeProfileForm()
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Add New Employee',
        'action': 'Create'
    }
    return render(request, 'employees/employee_form.html', context)


# 3. UPDATE (Edit Existing Employee)
@login_required
@admin_required
@transaction.atomic
def employee_update(request, pk):
    profile = get_object_or_404(EmployeeProfile, pk=pk)
    user = profile.user
    
    if request.method == 'POST':
        user_form = EmployeeUserForm(request.POST, instance=user)
        profile_form = EmployeeProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.info(request, f"Employee {user.get_full_name()}'s details updated.")
            return redirect('employee_list')
        else:
            # Handle form errors
            pass
    
    else: # GET request
        user_form = EmployeeUserForm(instance=user)
        # We blank out the password field on GET for security
        user_form.fields['password'].initial = '' 
        profile_form = EmployeeProfileForm(instance=profile)
        
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Update Employee Details',
        'action': 'Update',
        'employee_id': profile.employee_id
    }
    return render(request, 'employees/employee_form.html', context)


# 4. DELETE (Deactivate Employee) - Soft Delete Recommended
@login_required
@admin_required
def employee_delete(request, pk):
    profile = get_object_or_404(EmployeeProfile, pk=pk)
    user = profile.user
    
    if request.method == 'POST':
        # Soft delete: Deactivate the user instead of deleting the records
        user.is_active = False 
        user.save()
        messages.warning(request, f"Employee {user.get_full_name()} ({profile.employee_id}) has been deactivated (soft deleted).")
        return redirect('employee_list')

    # Confirmation page on GET (not implemented, but good practice)
    context = {'employee': profile, 'title': 'Confirm Deletion'}
    return render(request, 'employees/employee_confirm_delete.html', context)
