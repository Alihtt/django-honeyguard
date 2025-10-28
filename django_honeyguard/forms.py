from django import forms

from .conf import settings as honeyguard_settings
from .mixins import LoginFormMixin


class FakeDjangoLoginForm(forms.Form, LoginFormMixin):
    """Fake login form with hidden honeypot field to detect bots."""

    username = forms.CharField(
        max_length=honeyguard_settings.MAX_USERNAME_LENGTH,
        required=True,
        label="Username:",
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "autocapitalize": "none",
                "autocomplete": "username",
                "maxlength": str(honeyguard_settings.MAX_USERNAME_LENGTH),
                "required": True,
            }
        ),
    )

    password = forms.CharField(
        max_length=honeyguard_settings.MAX_PASSWORD_LENGTH,
        required=True,
        label="Password:",
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "maxlength": str(honeyguard_settings.MAX_PASSWORD_LENGTH),
                "required": True,
            }
        ),
    )

    # Hidden timing field to detect too-fast submissions
    form_render_time = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )

    def clean_username(self):
        """Validate username field."""
        username = self.cleaned_data.get("username", "").strip()
        if not username:
            raise forms.ValidationError("This field is required.")
        return username

    def clean_password(self):
        """Validate password field."""
        password = self.cleaned_data.get("password", "")
        if not password:
            raise forms.ValidationError("This field is required.")
        return password


class FakeWordPressLoginForm(LoginFormMixin, forms.Form):
    """Fake WordPress login form with WordPress-specific attributes."""

    username = forms.CharField(
        max_length=honeyguard_settings.WORDPRESS_USERNAME_MAX_LENGTH,
        required=True,
        label="Username or Email Address",
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "id": "user_login",
                "size": "20",
                "autocapitalize": "off",
                "autocomplete": "username",
                "maxlength": str(
                    honeyguard_settings.WORDPRESS_USERNAME_MAX_LENGTH
                ),
            }
        ),
    )
    password = forms.CharField(
        max_length=honeyguard_settings.WORDPRESS_PASSWORD_MAX_LENGTH,
        required=True,
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "input",
                "id": "user_pass",
                "size": "20",
                "autocomplete": "current-password",
                "maxlength": str(
                    honeyguard_settings.WORDPRESS_PASSWORD_MAX_LENGTH
                ),
            }
        ),
    )

    # Hidden timing field to detect too-fast submissions
    form_render_time = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )

    def clean_username(self):
        """Validate username field."""
        username = self.cleaned_data.get("username", "").strip()
        if not username:
            raise forms.ValidationError("The username field is empty.")
        return username

    def clean_password(self):
        """Validate password field."""
        password = self.cleaned_data.get("password", "")
        if not password:
            raise forms.ValidationError("The password field is empty.")
        return password
