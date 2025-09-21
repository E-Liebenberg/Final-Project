from django.urls import path
from . import views

app_name = 'remotes'

urlpatterns = [
    path('manage/', views.manage_remotes, name='manage_remotes'),
    path('add/', views.add_remote, name='add_remote'),
    path('edit/<int:remote_id>/', views.edit_remote, name='edit_remote'),
    path('delete/<int:remote_id>/', views.delete_remote, name='delete_remote'),
]