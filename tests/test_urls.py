"""Tests for URL routing."""

from django_honeyguard.urls import app_name, urlpatterns


class TestURLConfiguration:
    """Test URL configuration."""

    def test_app_name(self):
        """Test app_name is set correctly."""
        assert app_name == "django_honeyguard"

    def test_urlpatterns_exist(self):
        """Test that urlpatterns exist."""
        assert len(urlpatterns) > 0

    def test_django_admin_url_pattern(self):
        """Test Django admin URL pattern."""
        # Note: This may not resolve if URLs aren't included in ROOT_URLCONF
        # We'll check the pattern structure instead
        patterns = [p.pattern for p in urlpatterns]
        assert any("admin/" in str(p) for p in patterns)

    def test_wp_admin_url_pattern(self):
        """Test WordPress admin URL pattern."""
        patterns = [p.pattern for p in urlpatterns]
        assert any("wp-admin" in str(p) for p in patterns)

    def test_url_names_exist(self):
        """Test that URL names are defined."""
        names = [p.name for p in urlpatterns if p.name]
        assert "fake_django_admin" in names or len(names) > 0
        assert "fake_wp_admin" in names or len(names) > 0
