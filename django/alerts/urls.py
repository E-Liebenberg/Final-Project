from django.urls import path
from . import views

app_name = 'alerts'

urlpatterns = [
    path('', views.alert_dashboard, name='dashboard'),
    path('ack/<int:alert_id>/', views.acknowledge_alert, name='acknowledge'),
    path('full/', views.full_dashboard, name='dashboard_full'),
    path('create/', views.create_alert, name='create_alert'),
]
