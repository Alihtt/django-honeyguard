from django.urls import path

from .views import FakeDjangoAdminView, FakeWPAdminView

app_name = "django_honeyguard"

urlpatterns = [
    path("admin/", FakeDjangoAdminView.as_view(), name="fake_django_admin"),
    path("wp-admin.php", FakeWPAdminView.as_view(), name="fake_wp_admin"),
]
