from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Attendance
from datetime import date, timedelta
from calendar import monthrange, Calendar
from django.utils import timezone

@login_required
def attendance_mark(request):
    """Check-in / check-out for logged-in employee."""
    employee = request.user.profile  # Assuming a OneToOneField to EmployeeProfile
    today = date.today()
    
    # Get or create today's attendance
    attendance, created = Attendance.objects.get_or_create(employee=employee, date=today)

    action = request.GET.get("action")
    if action == "check_in" and not attendance.check_in_time:
        attendance.check_in_time = timezone.now().time()
        attendance.status = "P"
        attendance.save()
        messages.success(request, "Checked in successfully.")
    elif action == "check_out" and not attendance.check_out_time:
        attendance.check_out_time = timezone.now().time()
        attendance.save()
        messages.success(request, "Checked out successfully.")
    else:
        if action:
            messages.warning(request, "Action already performed or invalid.")

    return redirect(reverse("attendance:monthly_calendar_current"))


@login_required
def monthly_calendar(request, year=None, month=None):
    """Generate calendar view for logged-in employee."""
    employee = request.user.profile
    today = date.today()

    # Default to current month
    if not year or not month:
        year, month = today.year, today.month

    # Number of days in month
    _, num_days = monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, num_days)

    # Fetch attendance records for the month
    records = Attendance.objects.filter(employee=employee, date__range=[start_date, end_date])
    record_map = {r.date: r for r in records}

    # Generate calendar weeks (list of lists)
    cal = Calendar(firstweekday=0)  # Week starts on Monday
    month_weeks = cal.monthdatescalendar(year, month)

    calendar_weeks = []
    for week in month_weeks:
        week_data = []
        for day in week:
            if day.month != month:
                # Days outside current month
                week_data.append({"day": None})
            else:
                rec = record_map.get(day)
                week_data.append({
                    "day": day.day,
                    "date": day,
                    "status": rec.status if rec else "U",
                    "check_in": rec.check_in_time if rec else None,
                    "check_out": rec.check_out_time if rec else None,
                    "is_today": day == today,
                })
        calendar_weeks.append(week_data)

    # Previous and next month URLs
    prev_month_date = start_date - timedelta(days=1)
    next_month_date = end_date + timedelta(days=1)

    context = {
        "calendar_weeks": calendar_weeks,
        "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "month_name": start_date.strftime("%B"),
        "year": year,
        "prev_month_url": reverse("attendance:monthly_calendar", args=[prev_month_date.year, prev_month_date.month]),
        "next_month_url": reverse("attendance:monthly_calendar", args=[next_month_date.year, next_month_date.month]),
        "view_employee": employee,
    }
    return render(request, "attendance/monthly_calendar.html", context)
