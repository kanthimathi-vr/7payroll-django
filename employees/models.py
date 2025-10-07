from django.db import models

# Create your models here.
from django.db import models
from accounts.models import CustomUser

class EmployeeProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    employee_id = models.CharField(max_length=10, unique=True, verbose_name="Employee ID")
    department = models.CharField(max_length=50)
    job_title = models.CharField(max_length=50)
    
    # Financial fields (Final model design)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Basic Salary", null=True, blank=True)
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="H.R.A")
    other_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Other Allowance")
    pf_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="P.F. Deduction")
    tax_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Tax Deduction")
    
    # Other Details
    phone_number = models.CharField(max_length=15, blank=True)
    hire_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.employee_id})"

    @property
    def gross_monthly_pay(self):
        return self.basic_salary + self.hra + self.other_allowance

    @property
    def total_deductions(self):
        return self.pf_deduction + self.tax_deduction