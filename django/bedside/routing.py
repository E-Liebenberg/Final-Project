from django.urls import re_path
from bedside import consumers
websocket_urlpatterns = [
    re_path(r"ws/bedsidev3/dashboard/$", consumers.BedsideDashboardConsumer.as_asgi())
]
