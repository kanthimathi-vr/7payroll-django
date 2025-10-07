from employees.models import EmployeeProfile
from attendance.models import Attendance
from payroll.models import MonthlySalarySlip
from datetime import date, timedelta
from calendar import monthrange
from django.db import transaction

def calculate_monthly_payroll(employee_profile: EmployeeProfile, year: int, month: int):
    """
    Calculates the detailed salary components and net pay for a single employee
    for a given month and saves the MonthlySalarySlip record.
    """
    
    # 1. Determine Working Days and Attendance
    
    # Calculate total days in the month
    num_days_in_month = monthrange(year, month)[1]
    start_date = date(year, month, 1)
    end_date = date(year, month, num_days_in_month)
    
    # Fetch attendance records for the month
    attendance_records = Attendance.objects.filter(
        employee=employee_profile,
        date__year=year,
        date__month=month
    )
    
    present_days = attendance_records.filter(status='P').count()
    leave_days = attendance_records.filter(status='L').count()
    # Assume any day not marked Present or Leave is Absent or a non-working day placeholder.
    # For simplicity, we calculate absent days based on (total days - present - leave)
    # A robust system would track holidays and weekends separately.
    total_paid_days = present_days + leave_days 
    absent_days = num_days_in_month - total_paid_days # Days to be deducted, includes weekends if not marked P/L

    # 2. Financial Calculations
    
    # Get base components from the Employee Profile (Assumed Monthly figures)
    basic = employee_profile.basic_salary
    hra = employee_profile.hra
    other_allowance = employee_profile.other_allowance
    pf_deduction = employee_profile.pf_deduction
    tax_deduction = employee_profile.tax_deduction

    # Gross Earning (Total fixed components)
    gross_earning_fixed = basic + hra + other_allowance
    
    # Calculate Payable Gross (Adjusted for absent days)
    # Deduct a proportional amount based on absent days
    daily_gross_rate = gross_earning_fixed / num_days_in_month
    
    total_deduction_for_absence = absent_days * daily_gross_rate
    
    gross_salary = gross_earning_fixed - total_deduction_for_absence
    
    # Total Deductions (Fixed deductions + Absence Deduction)
    total_deductions = pf_deduction + tax_deduction + total_deduction_for_absence
    
    # Net Salary
    net_salary = gross_salary - (pf_deduction + tax_deduction)

    # 3. Create or Update Salary Slip Record
    
    month_year_date = date(year, month, 1)

    slip, created = MonthlySalarySlip.objects.update_or_create(
        employee=employee_profile,
        month_year=month_year_date,
        defaults={
            'total_working_days': num_days_in_month,
            'present_days': present_days,
            'absent_days': absent_days,
            'leave_days': leave_days,
            'gross_salary': round(gross_salary, 2),
            'total_deductions': round(total_deductions, 2),
            'net_salary': round(net_salary, 2),
            # 'generated_by': request.user (will be set in the view)
        }
    )
    
    return slip, created, gross_salary, net_salary, total_deductions

@transaction.atomic
def generate_payroll_for_all(user, year, month):
    """Generates payroll slips for all active employees."""
    active_employees = EmployeeProfile.objects.filter(user__is_active=True)
    generated_count = 0
    
    for profile in active_employees:
        slip, created, _, _, _ = calculate_monthly_payroll(profile, year, month)
        slip.generated_by = user
        slip.save()
        generated_count += 1
        
    return generated_count
