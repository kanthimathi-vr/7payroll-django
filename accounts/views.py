from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from employees.models import EmployeeProfile
from attendance.models import Attendance
from payroll.models import MonthlySalarySlip
from datetime import date
from django.db.models import Sum, Q

@login_required
def dashboard_view(request):
    user = request.user
    today = date.today()
    
    # Context dictionary to hold all dashboard data
    context = {}

    if user.role == 'ADMIN':
        # --- ADMIN DASHBOARD LOGIC ---
        
        # 1. Employee Stats
        total_employees = EmployeeProfile.objects.filter(user__is_active=True).count()
        new_hires_this_month = EmployeeProfile.objects.filter(
            hire_date__year=today.year, 
            hire_date__month=today.month,
            user__is_active=True
        ).count()
        
        # 2. Attendance Stats (Today)
        # Get employees who have checked in today
        present_today_count = Attendance.objects.filter(
            date=today, 
            status='P'
        ).count()
        
        # Calculate absent/unmarked employees
        absent_or_unmarked_today = total_employees - present_today_count
        
        # 3. Payroll Stats
        current_month_start = date(today.year, today.month, 1)
        
        # Count pending slips (not marked as paid)
        pending_payrolls = MonthlySalarySlip.objects.filter(
            month_year=current_month_start,
            is_paid=False
        ).count()
        
        # Calculate total net salary generated for this month
        total_net_salary = MonthlySalarySlip.objects.filter(
            month_year=current_month_start
        ).aggregate(Sum('net_salary'))['net_salary__sum'] or 0
        
        context.update({
            'is_admin': True,
            'total_employees': total_employees,
            'new_hires_this_month': new_hires_this_month,
            'present_today_count': present_today_count,
            'absent_or_unmarked_today': absent_or_unmarked_today,
            'pending_payrolls': pending_payrolls,
            'total_net_salary': total_net_salary,
        })
        
    elif user.role == 'EMPLOYEE':
        # --- EMPLOYEE DASHBOARD LOGIC ---
        try:
            profile = user.profile
            current_month_start = date(today.year, today.month, 1)
            
            # 1. Attendance Stats (This Month)
            attendance_qs = Attendance.objects.filter(
                employee=profile,
                date__year=today.year,
                date__month=today.month
            )
            present_days = attendance_qs.filter(status='P').count()
            absent_days = attendance_qs.filter(status='A').count()
            leave_days = attendance_qs.filter(status='L').count()
            
            # 2. Last Salary Slip
            last_slip = MonthlySalarySlip.objects.filter(employee=profile).order_by('-month_year').first()
            
            context.update({
                'is_employee': True,
                'profile': profile,
                'present_days': present_days,
                'absent_days': absent_days,
                'leave_days': leave_days,
                'last_slip': last_slip,
            })
            
        except EmployeeProfile.DoesNotExist:
            # Handle case where a user is created but no profile exists
            messages.error(request, "Your employee profile is incomplete. Please contact HR/Admin.")
            
    return render(request, 'dashboard.html', context)


