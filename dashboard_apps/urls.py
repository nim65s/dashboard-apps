"""Main URL configuration."""

from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user-authorization-callback', views.log),
    path('webhook', views.github_webhook),
    path('gh', views.github_webhook),
    path('', views.log),
]
