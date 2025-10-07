from django import forms
from .models import Attendance

class AttendanceManualForm(forms.ModelForm):
    """Form for Admin/HR to manually mark or correct an attendance record."""
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'status', 'check_in_time', 'check_out_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_in_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'check_out_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'employee': forms.Select(attrs={'class': 'form-select'}),
        }