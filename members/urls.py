from django.urls import path
from . import views  # Ye 'members' folder ke andar hai, isliye yahan views mil jayega

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add, name='add'),
    path('add/addrecord/', views.addrecord, name='addrecord'),
    path('delete/<int:id>', views.delete, name='delete'),
    path('update/<int:id>', views.update, name='update'),
    path('updaterecord/<int:id>', views.updaterecord, name='updaterecord'),
    
    # Library ka rasta
    path('library/', views.library, name='library'),
    path('attendance/', views.attendance, name='attendance'),
    path('attendance_records/', views.attendance_records, name='attendance_records'),
]