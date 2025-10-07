# employees/signals.py (Modified)

from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUser
from .models import EmployeeProfile
from datetime import date # Import date if not already there

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Provide default values for ALL required fields (basic_salary, hire_date, employee_id, etc.)
        EmployeeProfile.objects.create(
            user=instance,
            # CONFIRMED REQUIRED FIELDS:
            basic_salary=0.00,        # Setting a default value to satisfy the NOT NULL constraint
            hire_date=date.today(),   # Setting the current date to satisfy the NOT NULL constraint
            
            # **IMPORTANT:** If 'employee_id' is also required and doesn't have a default, 
            # you must add a placeholder here as well. Example:
            employee_id=f'TEMP-{instance.pk}' 
        )

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except EmployeeProfile.DoesNotExist:
        pass # The profile doesn't exist yet, which is fine