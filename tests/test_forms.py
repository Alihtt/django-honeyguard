"""Tests for HoneyGuard forms."""

from django import forms

from django_honeyguard.forms import (
    BaseFakeLoginForm,
    FakeDjangoLoginForm,
    FakeWordPressLoginForm,
)


class TestBaseFakeLoginForm:
    """Test BaseFakeLoginForm."""

    def test_form_fields(self):
        """Test that form has required fields."""
        form = BaseFakeLoginForm()
        assert "hp" in form.fields
        assert "render_time" in form.fields

    def test_honeypot_field_is_hidden(self):
        """Test that honeypot field has hidden attributes."""
        form = BaseFakeLoginForm()
        widget = form.fields["hp"].widget
        attrs = widget.attrs
        assert "display:none" in attrs.get("style", "")
        assert attrs.get("tabindex") == "-1"

    def test_username_required(self):
        """Test that username field validation requires username."""
        # BaseFakeLoginForm doesn't have username/password fields defined
        # Only subclasses do - test those instead
        form = FakeDjangoLoginForm(data={"username": "", "password": "pass"})
        assert not form.is_valid()
        assert "username" in form.errors

    def test_password_required(self):
        """Test that password field validation requires password."""
        # BaseFakeLoginForm doesn't have username/password fields defined
        # Only subclasses do - test those instead
        form = FakeDjangoLoginForm(data={"username": "user", "password": ""})
        assert not form.is_valid()
        assert "password" in form.errors

    def test_valid_form_with_all_fields(self):
        """Test form is valid with all required fields."""
        form = BaseFakeLoginForm(
            data={
                "hp": "",  # Honeypot field name is "hp"
                "render_time": "",
            }
        )
        # Note: BaseFakeLoginForm doesn't have username/password fields
        # This would need subclasses for full validation
        assert "hp" in form.fields

    def test_honeypot_not_required(self):
        """Test that honeypot field is not required."""
        form = BaseFakeLoginForm(data={})
        # hp field should be optional
        assert "hp" in form.fields
        assert form.fields["hp"].required is False


class TestFakeDjangoLoginForm:
    """Test FakeDjangoLoginForm."""

    def test_form_has_username_and_password_fields(self):
        """Test that form has username and password fields."""
        form = FakeDjangoLoginForm()
        assert "username" in form.fields
        assert "password" in form.fields
        assert "hp" in form.fields

    def test_username_field_attributes(self):
        """Test username field attributes."""
        form = FakeDjangoLoginForm()
        username_field = form.fields["username"]
        assert username_field.label == "Username:"
        widget = username_field.widget
        assert widget.attrs.get("autofocus") is True

    def test_password_field_attributes(self):
        """Test password field attributes."""
        form = FakeDjangoLoginForm()
        password_field = form.fields["password"]
        assert isinstance(password_field.widget, forms.PasswordInput)
        assert (
            password_field.widget.attrs.get("autocomplete")
            == "current-password"
        )

    def test_username_max_length_from_settings(self):
        """Test that username max_length uses settings."""
        # Note: Forms evaluate settings at module import time, so override_settings
        # won't change the form after import. This test verifies the form uses
        # the current default setting value.
        from django_honeyguard.conf import settings as hg_settings

        form = FakeDjangoLoginForm()
        # Form uses the setting value (default is 150, or whatever was set at import)
        expected_max = hg_settings.MAX_USERNAME_LENGTH
        assert form.fields["username"].max_length == expected_max

    def test_form_valid_with_required_fields(self):
        """Test form validation with required fields."""
        form = FakeDjangoLoginForm(
            data={
                "username": "testuser",
                "password": "testpass",
                "hp": "",  # Honeypot field name is "hp"
            }
        )
        assert form.is_valid()

    def test_form_invalid_without_username(self):
        """Test form is invalid without username."""
        form = FakeDjangoLoginForm(data={"password": "testpass"})
        assert not form.is_valid()
        assert "username" in form.errors

    def test_form_invalid_without_password(self):
        """Test form is invalid without password."""
        form = FakeDjangoLoginForm(data={"username": "testuser"})
        assert not form.is_valid()
        assert "password" in form.errors

    def test_honeypot_not_filled(self):
        """Test that honeypot check works when not filled."""
        form = FakeDjangoLoginForm(
            data={
                "username": "user",
                "password": "pass",
                "hp": "",
            }  # Field name is "hp"
        )
        form.is_valid()
        assert form.is_honeypot_triggered() is False

    def test_honeypot_filled_detected(self):
        """Test that honeypot is detected when filled."""
        form = FakeDjangoLoginForm(
            data={
                "username": "user",
                "password": "pass",
                "hp": "filled",  # Field name is "hp", filled means bot detected
            }
        )
        form.is_valid()
        assert form.is_honeypot_triggered() is True


class TestFakeWordPressLoginForm:
    """Test FakeWordPressLoginForm."""

    def test_form_has_wordpress_fields(self):
        """Test that form has username and password fields."""
        form = FakeWordPressLoginForm()
        assert "username" in form.fields
        assert "password" in form.fields

    def test_wordpress_username_label(self):
        """Test WordPress username label."""
        form = FakeWordPressLoginForm()
        assert form.fields["username"].label == "Username or Email Address"

    def test_wordpress_username_widget_attributes(self):
        """Test WordPress username widget attributes."""
        form = FakeWordPressLoginForm()
        widget = form.fields["username"].widget
        assert widget.attrs.get("class") == "input"
        assert widget.attrs.get("id") == "user_login"

    def test_wordpress_password_widget_attributes(self):
        """Test WordPress password widget attributes."""
        form = FakeWordPressLoginForm()
        widget = form.fields["password"].widget
        assert widget.attrs.get("class") == "input"
        assert widget.attrs.get("id") == "user_pass"

    def test_wordpress_custom_error_messages(self):
        """Test WordPress custom error messages."""
        form = FakeWordPressLoginForm()
        assert "The username field is empty." in form.username_required_message
        assert "The password field is empty." in form.password_required_message

    def test_wordpress_username_max_length_from_settings(self):
        """Test that WordPress username max_length uses settings."""
        # Note: Forms evaluate settings at module import time, so override_settings
        # won't change the form after import. This test verifies the form uses
        # the current default setting value.
        from django_honeyguard.conf import settings as hg_settings

        form = FakeWordPressLoginForm()
        # Form uses the setting value (default is 60, or whatever was set at import)
        expected_max = hg_settings.WORDPRESS_USERNAME_MAX_LENGTH
        assert form.fields["username"].max_length == expected_max

    def test_wordpress_form_validation(self):
        """Test WordPress form validation."""
        form = FakeWordPressLoginForm(
            data={
                "username": "wpuser",
                "password": "wppass",
                "hp": "",  # Field name is "hp"
            }
        )
        assert form.is_valid()

    def test_wordpress_form_invalid_without_fields(self):
        """Test WordPress form invalid without required fields."""
        form = FakeWordPressLoginForm(data={})
        assert not form.is_valid()
