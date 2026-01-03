from django.urls import path
from . import views

urlpatterns = [
    # --- Main Student Operations (CRUD) ---
    path('', views.index, name='index'),
    path('add/', views.add, name='add'),
    path('details/<int:id>/', views.details, name='details'),
    path('update/<int:id>/', views.update, name='update'),
    path('delete/<int:id>/', views.delete, name='delete'),

    # --- Authentication (Login/Logout) ---
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
]