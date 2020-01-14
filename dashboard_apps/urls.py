"""Main URL configuration."""

from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user-authorization-callback', views.log),
    path('gh', views.github_webhook),
    path('gl', views.gitlab_webhook),
    path('', views.log),
]
