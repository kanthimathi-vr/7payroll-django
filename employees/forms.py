from django import forms
from employees.models import EmployeeProfile
from accounts.models import CustomUser

class EmployeeUserForm(forms.ModelForm):
    # This form is for the CustomUser basic details
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'username', 'role', 'is_active', 'password')
        widgets = {
            # Ensure role field defaults to 'EMPLOYEE' for new users if not set by admin
            'role': forms.Select(choices=[('EMPLOYEE', 'Employee'), ('ADMIN', 'Admin')]),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class EmployeeProfileForm(forms.ModelForm):
    # This form is for the EmployeeProfile details
    class Meta:
        model = EmployeeProfile
        # Exclude 'user' field as it is set separately.
        fields = (
            'employee_id', 'department', 'job_title', 'basic_salary', 
            'hra', 'other_allowance', 'pf_deduction', 'tax_deduction', 
            'phone_number', 'hire_date'
        )
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }