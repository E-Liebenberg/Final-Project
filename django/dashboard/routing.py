# dashboard/routing.py

from django.urls import re_path
from . import consumers  # Ensure this line is present

websocket_urlpatterns = [
    re_path(r'ws/dashboard/(?P<remote_id>[^/]+)/$', consumers.DashboardConsumer.as_asgi()),
]