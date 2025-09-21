from django.urls import path
from .views import dashboard_view, toggle_led, theatre_history, download_csv

app_name = "theatre"

urlpatterns = [
    path("dashboard/", dashboard_view, name="theatre_dashboard"),
    path("toggle_led/", toggle_led, name="toggle_led"),
    path("history/", theatre_history, name="theatre_history"),
    path("download_csv/", download_csv, name="download_csv"),

]
