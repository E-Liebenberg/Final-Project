# accounts/urls.py

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.user_admin_panel, name='user_admin_panel'),
    path('create/', views.create_user, name='create_user'),
    path('edit/<int:user_id>/', views.edit_user, name='edit_user'),
]
