"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from project.views import home
from django.shortcuts import redirect
from .views import mqtt_publish_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/admin/', include('accounts.urls')), 
    path("dashboard/", include("dashboard.urls")),
    path('', home, name='home'), 
    path('patients/', include('patients.urls')),  
    path('admin_clerk/', include('admin_clerk.urls')),
    path('nurse/', include('nurse.urls')),
    path('doctors/', include('doctors.urls')),
    path('alerts/', include('alerts.urls')),
    path('remotes/', include('remotes.urls')),
    path('login/', lambda request: redirect('/accounts/login/', permanent=True)),
    path('theatre/', include('theatre.urls')),  
    path('bedside/', include('bedside.urls')), 
    path("api/mqtt/publish/", mqtt_publish_view, name="mqtt_publish"),  
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])