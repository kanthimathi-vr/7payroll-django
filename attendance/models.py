from django.db import models
from employees.models import EmployeeProfile

class Attendance(models.Model):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)

    STATUS_CHOICES = [
        ('P', 'Present'),
        ('A', 'Absent'),
        ('L', 'Leave'),
        ('U', 'Unmarked'),
    ]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='U')

    class Meta:
        unique_together = ('employee', 'date')
        verbose_name_plural = "Attendance Records"

    def __str__(self):
        return f"{self.employee.employee_id} on {self.date} - {self.get_status_display()}"
