from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from employees.models import EmployeeProfile 
from datetime import date

# This field name is confirmed correct now
DATE_FIELD_NAME = 'hire_date' 
BASIC_SALARY_FIELD = 50000.00 # Default salary value to satisfy constraints if not null

class Command(BaseCommand):
    help = 'Creates 5 default non-superuser employee profiles, or creates profiles for existing users if missing.'

    def handle(self, *args, **kwargs):
        # 1. Define the default employees data
        employee_data = [
            {'username': 'alice', 'email': 'alice@example.com', 'password': 'testpassword', 
             'employee_id': 'EMP001', 'job_title': 'Software Engineer', 'department': 'Technology'},
             
            {'username': 'bob', 'email': 'bob@example.com', 'password': 'testpassword', 
             'employee_id': 'EMP002', 'job_title': 'HR Manager', 'department': 'Human Resources'},
             
            {'username': 'charlie', 'email': 'charlie@example.com', 'password': 'testpassword', 
             'employee_id': 'EMP003', 'job_title': 'Sales Representative', 'department': 'Sales'},
             
            {'username': 'diana', 'email': 'diana@example.com', 'password': 'testpassword', 
             'employee_id': 'EMP004', 'job_title': 'Financial Analyst', 'department': 'Finance'},
             
            {'username': 'eve', 'email': 'eve@example.com', 'password': 'testpassword', 
             'employee_id': 'EMP005', 'job_title': 'Product Designer', 'department': 'Design'},
        ]

        created_users_count = 0
        created_profiles_count = 0
        
        for data in employee_data:
            username = data['username']
            
            try:
                # Attempt to get the user if they already exist
                user = CustomUser.objects.get(username=username)
                self.stdout.write(self.style.WARNING(f"User {username} already exists. Checking for missing profile..."))
                
            except CustomUser.DoesNotExist:
                # User does not exist, so create both the user and the profile
                user = CustomUser.objects.create_user(
                    username=username,
                    email=data['email'],
                    password=data['password']
                )
                self.stdout.write(self.style.SUCCESS(f"Successfully created user: {username}"))
                created_users_count += 1
            
            # --- PROFILE CREATION/CHECK LOGIC ---
            
            # 1. Check if the profile already exists (Using the CORRECT ACCESSOR: user.profile)
            try:
                # If the profile exists, this line will succeed.
                _ = user.profile 
                self.stdout.write(self.style.NOTICE(f"Profile for {username} already exists. Skipping profile creation."))
            
            except EmployeeProfile.DoesNotExist:
                # 2. If the profile is missing, create it now for the existing user
                
                # Check if the user was created *without* their profile (the previous error scenario)
                self.stdout.write(self.style.NOTICE(f"Creating missing profile for existing user: {username}"))
                
                profile_kwargs = {
                    'user': user,
                    'employee_id': data['employee_id'],
                    'job_title': data['job_title'],
                    'department': data['department'],
                    DATE_FIELD_NAME: date.today(),
                    'basic_salary': BASIC_SALARY_FIELD 
                }
                
                # Create the EmployeeProfile instance
                EmployeeProfile.objects.create(**profile_kwargs)
                
                self.stdout.write(self.style.SUCCESS(f"Successfully created missing profile for: {username}"))
                created_profiles_count += 1


        self.stdout.write(self.style.SUCCESS(f"\n--- Script Summary ---"))
        self.stdout.write(self.style.SUCCESS(f"Users created: {created_users_count}"))
        self.stdout.write(self.style.SUCCESS(f"Missing profiles created: {created_profiles_count}"))
