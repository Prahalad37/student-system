"""
Super Admin URL Configuration
"""

from django.urls import path
from members.views.super_admin import (
    SuperAdminLoginView,
    super_admin_dashboard,
    create_demo_school,
    populate_demo_data,
    school_list,
    toggle_school_status,
)

app_name = 'super_admin'

urlpatterns = [
    path('login/', SuperAdminLoginView.as_view(), name='login'),
    path('dashboard/', super_admin_dashboard, name='dashboard'),
    path('schools/', school_list, name='school_list'),
    path('schools/create-demo/', create_demo_school, name='create_demo'),
    path('schools/<int:school_id>/populate/', populate_demo_data, name='populate_demo_data'),
    path('schools/<int:school_id>/toggle-status/', toggle_school_status, name='toggle_status'),
]
