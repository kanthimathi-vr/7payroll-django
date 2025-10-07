from django.db import models

# Create your models here.
from django.db import models
from employees.models import EmployeeProfile
from accounts.models import CustomUser # Import CustomUser

class MonthlySalarySlip(models.Model):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='salary_slips')
    month_year = models.DateField(verbose_name="Pay Month")
    
    # Attendance Summary
    total_working_days = models.IntegerField(default=30)
    present_days = models.IntegerField(default=0)
    absent_days = models.IntegerField(default=0)
    leave_days = models.IntegerField(default=0)
    
    # Financial Summary
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Audit trail
    generated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('employee', 'month_year')
        ordering = ['-month_year']
        verbose_name = "Monthly Salary Slip"
        
    def __str__(self):
        return f"Slip for {self.employee.employee_id} - {self.month_year.strftime('%B %Y')}"
    