"""
dashboard_apps URL Configuration
"""

from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user-authorization-callback', views.log),
    path('webhook', views.webhook),
    path('', views.log),
]
