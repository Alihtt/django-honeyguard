from typing import Any

from django import forms

from .conf import settings as honeyguard_settings


class BaseFakeLoginForm(forms.Form):
    username_required_message = "This field is required."
    password_required_message = "This field is required."

    hp = forms.CharField(
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "style": "display:none !important; position: absolute; left: -9999px;",
                "tabindex": "-1",
                "autocomplete": "off",
                "aria-hidden": "true",
            }
        ),
    )
    render_time = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )

    def is_honeypot_triggered(self) -> bool:
        """Check if the honeypot field was filled (indicating bot activity)."""
        return bool(self.data.get("hp", "").strip())

    def clean_username(self) -> str:
        """Clean and validate username field."""
        username = self.cleaned_data.get("username", "").strip()
        if not username:
            raise forms.ValidationError(self.username_required_message)
        return username

    def clean_password(self) -> str:
        """Clean and validate password field."""
        password = self.cleaned_data.get("password", "")
        if not password:
            raise forms.ValidationError(self.password_required_message)
        return password


class FakeDjangoLoginForm(BaseFakeLoginForm):
    """Fake login form with hidden honeypot field to detect bots."""

    username = forms.CharField(
        max_length=honeyguard_settings.MAX_USERNAME_LENGTH,
        label="Username:",
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "autocapitalize": "none",
                "autocomplete": "username",
                "maxlength": str(honeyguard_settings.MAX_USERNAME_LENGTH),
            }
        ),
    )

    password = forms.CharField(
        max_length=honeyguard_settings.MAX_PASSWORD_LENGTH,
        label="Password:",
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "maxlength": str(honeyguard_settings.MAX_PASSWORD_LENGTH),
            }
        ),
    )


class FakeWordPressLoginForm(BaseFakeLoginForm):
    """Fake WordPress login form with WordPress-specific attributes."""

    username_required_message = "The username field is empty."
    password_required_message = "The password field is empty."

    username = forms.CharField(
        max_length=honeyguard_settings.WORDPRESS_USERNAME_MAX_LENGTH,
        label="Username or Email Address",
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "id": "user_login",
                "size": "20",
                "autocapitalize": "off",
                "autocomplete": "username",
                "maxlength": str(honeyguard_settings.WORDPRESS_USERNAME_MAX_LENGTH),
            }
        ),
    )
    password = forms.CharField(
        max_length=honeyguard_settings.WORDPRESS_PASSWORD_MAX_LENGTH,
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "input",
                "id": "user_pass",
                "size": "20",
                "autocomplete": "current-password",
                "maxlength": str(honeyguard_settings.WORDPRESS_PASSWORD_MAX_LENGTH),
            }
        ),
    )
