from django.urls import path
from .views import publish_command
from .views import remote_dashboard, publish_command

from . import views

urlpatterns = [
    path('publish/', publish_command, name='publish_command'),
    # path('remote/<str:mac>/', remote_dashboard, name='remote_dashboard'),
    path('remote/<str:remote_id>/', remote_dashboard, name='remote_dashboard'),
    path('publish/', publish_command, name='publish_command'),
]
