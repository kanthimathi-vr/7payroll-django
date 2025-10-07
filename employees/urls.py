from django.urls import path
from . import views

urlpatterns = [
    # READ: List all active employees
    path('', views.employee_list, name='employee_list'), 
    
    # CREATE: Add new employee
    path('add/', views.employee_create, name='employee_create'), 
    
    # UPDATE: Edit employee by primary key (pk)
    path('edit/<int:pk>/', views.employee_update, name='employee_update'), 
    
    # DELETE: Soft delete employee (deactivate)
    path('delete/<int:pk>/', views.employee_delete, name='employee_delete'), 
]

