from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("secret/", admin.site.urls),
    path("", include("django_honeyguard.urls")),  # Honeypot URLs
]
