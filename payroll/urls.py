from django.urls import path
from . import views

app_name = "payroll"  # <-- add this line

urlpatterns = [
    # READ: List all slips (Admin) or user's slips (Employee)
    path('', views.payroll_list, name='payroll_slips'), 
    
    # CREATE/UPDATE: Trigger bulk generation (Admin Only)
    path('generate/', views.payroll_generate, name='payroll_generate'), 
    
    # READ: Detailed slip view
    path('slip/<int:pk>/', views.salary_slip_detail, name='salary_slip_detail'), 
    
    # EXPORT: PDF View
    path('slip/<int:pk>/pdf/', views.export_slip_pdf, name='export_slip_pdf'), 
]
