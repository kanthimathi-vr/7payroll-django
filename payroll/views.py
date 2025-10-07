from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from datetime import date
from employees.models import EmployeeProfile
from .models import MonthlySalarySlip
from .utils import generate_payroll_for_all
from accounts.decorators import admin_required

# 1. LIST PAYROLL SLIPS (Admin sees all, Employee sees own)
@login_required
def payroll_list(request):
    if request.user.role == 'ADMIN':
        slips = MonthlySalarySlip.objects.all().order_by('-month_year', 'employee__employee_id')
        title = "All Payroll Slips"
        can_generate = True
    else: # Employee Role
        try:
            profile = request.user.profile
            slips = MonthlySalarySlip.objects.filter(employee=profile).order_by('-month_year')
            title = "My Pay Slips"
            can_generate = False
        except EmployeeProfile.DoesNotExist:
            messages.error(request, "Employee profile not found.")
            return redirect('dashboard')
    
    context = {
        'slips': slips,
        'title': title,
        'can_generate': can_generate
    }
    return render(request, 'payroll/payroll_list.html', context)


# 2. GENERATE PAYROLL (Admin Only)
@login_required
@admin_required
def payroll_generate(request):
    today = date.today()
    
    # Default to last month if it's early in the month, or current month if late
    default_date = today.replace(day=1) - timedelta(days=1)
    
    # Get selected month/year from form/URL or use default
    year = int(request.POST.get('year', default_date.year))
    month = int(request.POST.get('month', default_date.month))
    
    if request.method == 'POST':
        try:
            generated_count = generate_payroll_for_all(request.user, year, month)
            messages.success(request, f"Successfully generated/updated {generated_count} payroll slips for {date(year, month, 1).strftime('%B %Y')}.")
        except Exception as e:
            messages.error(request, f"Payroll generation failed: {e}")
            
        return redirect('payroll_list')

    # GET Request: Confirmation Page
    context = {
        'year': year,
        'month': month,
        'month_name': date(year, month, 1).strftime('%B %Y'),
        'title': 'Generate Monthly Payroll'
    }
    return render(request, 'payroll/payroll_confirm.html', context)


# 3. DISPLAY SLIP DETAIL (HTML View - Basis for PDF/Print)
@login_required
def salary_slip_detail(request, pk):
    slip = get_object_or_404(MonthlySalarySlip.objects.select_related('employee__user'), pk=pk)
    
    # Security check: Employee can only view their own slip
    if request.user.role == 'EMPLOYEE' and slip.employee.user != request.user:
        messages.error(request, "You do not have permission to view this pay slip.")
        return redirect('payroll_list')

    # Re-calculate gross/deductions breakdown for display
    profile = slip.employee
    gross_earning_fixed = profile.basic_salary + profile.hra + profile.other_allowance
    fixed_deductions = profile.pf_deduction + profile.tax_deduction
    
    # Calculate absence deduction amount (for detail display)
    daily_gross_rate = gross_earning_fixed / slip.total_working_days
    absence_deduction = slip.absent_days * daily_gross_rate

    context = {
        'slip': slip,
        'profile': profile,
        'gross_earning_fixed': gross_earning_fixed,
        'fixed_deductions': fixed_deductions,
        'absence_deduction': absence_deduction,
        'title': f"Salary Slip - {slip.month_year.strftime('%B %Y')}"
    }
    return render(request, 'payroll/salary_slip_detail.html', context)
    
    
# 4. EXPORT TO PDF (Placeholder using basic HTML structure)
# NOTE: Full PDF generation requires an external library (e.g., WeasyPrint, ReportLab).
# For now, we will just use the HTML detail view and note the dependency.
# This function serves as the endpoint trigger.
@login_required
def export_slip_pdf(request, pk):
    # In a production system:
    # 1. Fetch slip details
    # 2. Render 'payroll/salary_slip_pdf.html' (a print-optimized template)
    # 3. Use WeasyPrint/xhtml2pdf to convert the HTML to PDF
    # 4. Return the PDF file as an HTTP response
    messages.info(request, "PDF Export requires an external library (e.g., WeasyPrint). Displaying printable HTML view instead.")
    return salary_slip_detail(request, pk)