from django.urls import path  # <--- Ye line missing thi
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add, name='add'),  # Add wala URL
    path('details/<int:id>/', views.details, name='details'),
]
urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add, name='add'),
    path('details/<int:id>/', views.details, name='details'),
    path('delete/<int:id>/', views.delete, name='delete'), # <--- Ye nayi line
    path('update/<int:id>/', views.update, name='update'),
]