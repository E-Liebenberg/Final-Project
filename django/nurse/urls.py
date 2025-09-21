# nurse/urls.py

from django.urls import path
from . import views

app_name = 'nurse'

urlpatterns = [
    path('', views.nurse_dashboard, name='nurse_dashboard'),
    path('assign-remote/<int:patient_id>/', views.assign_remote_to_patient, name='assign_remote'),
    path('edit-remote/<int:patient_id>/', views.edit_remote, name='edit_remote'),
    path('remove-remote/<int:patient_id>/', views.remove_remote, name='remove_remote'),
    path('bill-stock/<int:patient_id>/', views.bill_stock_to_patient, name='bill_stock'),
    path('patient/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    path('patient/<int:patient_id>/note/add/', views.add_nurse_note, name='add_nurse_note'),

]
