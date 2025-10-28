from django import forms


class LoginFormMixin:
    # Hidden honeypot field - bots often fill all fields
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

    def is_honeypot_triggered(self):
        """Check if the honeypot field was filled (indicating bot activity)."""
        return bool(self.data.get("hp", "").strip())
