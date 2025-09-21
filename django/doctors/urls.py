# doctors/urls.py
from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('', views.doctors_dashboard, name='doctors_dashboard'),
    path('patient/<int:patient_id>/note/add/', views.add_doctor_note, name='add_doctor_note'),

]
