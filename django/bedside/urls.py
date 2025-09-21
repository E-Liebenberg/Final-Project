from django.urls import path
from .views import BedsideDashboardView, download_csv

urlpatterns = [
    path("dashboard/", BedsideDashboardView.as_view(), name="bedside_dashboard"),
    path("download_csv/", download_csv, name="bedside_download_csv"),
]
