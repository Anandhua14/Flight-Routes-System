"""
URL configuration for flight_routes project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('routes.urls')),
]
