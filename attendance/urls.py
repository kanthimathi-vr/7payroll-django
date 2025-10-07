from django.urls import path
from . import views

app_name = "attendance"

urlpatterns = [
    path("mark/", views.attendance_mark, name="mark_attendance"),
    path("calendar/", views.monthly_calendar, name="monthly_calendar_current"),
    path("calendar/<int:year>/<int:month>/", views.monthly_calendar, name="monthly_calendar"),
]

