from django.urls import path
from . import views

app_name = 'admin_clerk'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('edit/<int:patient_id>/', views.edit_patient, name='edit_patient'),
    path('admit/', views.admit_new_patient, name='admit_new_patient'),

]