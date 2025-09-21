from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('admit/', views.admit_patient, name='admit_patient'),
    path('pending/', views.pending_admissions, name='pending_admissions'),
    path('confirm/<int:patient_id>/', views.confirm_admission, name='confirm_admission'),
    path('dashboard/', views.patient_dashboard, name='dashboard'),
]
