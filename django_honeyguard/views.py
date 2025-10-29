"""Views for fake admin pages (honeypots)."""

from datetime import datetime
from typing import Any, Dict, Optional

from django.contrib import messages
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.forms import BaseForm
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.views.generic.edit import FormView

from .conf import settings as honeyguard_settings
from .forms import FakeDjangoLoginForm, FakeWordPressLoginForm
from .loggers import get_logger
from .signals import honeypot_triggered

logger = get_logger(__name__)


class FakeAdminView(FormView):
    """Base view for fake admin pages that act as honeypots."""

    success_url = "/"
    error_message = "Authentication failed."

    def get_error_message(self) -> str:
        """
        Get error message to display to user.

        Override in subclasses to provide specific error messages.

        Returns:
            str: Error message text
        """
        return self.error_message

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the view with a TimestampSigner."""
        super().__init__(*args, **kwargs)
        self.signer: TimestampSigner = TimestampSigner()
        self.signed_time: str = ""

    def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        """Store signed render time for timing detection."""
        render_time = timezone.now()
        # Sign the ISO string representation of the datetime
        self.signed_time = self.signer.sign(render_time.isoformat())
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self) -> Dict[str, Any]:
        """Get initial form data including signed render time."""
        initial = super().get_initial()
        initial["render_time"] = self.signed_time
        return initial

    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        """Handle GET requests - optionally trigger honeypot detection."""
        if honeyguard_settings.ENABLE_GET_METHOD_DETECTION:
            self.process_honeypot_trigger(request)

        return super().get(request, *args, **kwargs)

    def post(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        """Handle POST requests - always show error message."""
        response = super().post(request, *args, **kwargs)
        messages.error(request, self.get_error_message())
        return response

    def form_valid(self, form: BaseForm) -> HttpResponse:
        """Handle valid form submission - always trigger honeypot detection."""
        self.process_honeypot_trigger(
            self.request,
            form_data=form.cleaned_data,
        )
        return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form: BaseForm) -> HttpResponse:
        """Handle invalid form submission - still trigger honeypot detection."""
        self.process_honeypot_trigger(self.request, form_data=form.data)
        return self.render_to_response(self.get_context_data(form=form))

    def process_honeypot_trigger(
        self, request: HttpRequest, form_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Process honeypot trigger and send signal."""
        if not form_data:
            form_data = {}

        render_time = form_data.get("render_time")
        if render_time:
            try:
                # Unsign the ISO string and convert back to datetime then to ISO for consistency
                unsigned_str = self.signer.unsign(render_time, max_age=600)

                unsigned_dt = datetime.fromisoformat(unsigned_str)
                if timezone.is_naive(unsigned_dt):
                    unsigned_dt = timezone.make_aware(unsigned_dt)
                form_data["render_time"] = unsigned_dt.isoformat()
            except (SignatureExpired, BadSignature) as e:
                logger.warning(f"Invalid render_time signature: {e}")
                form_data["render_time"] = None
            except (ValueError, TypeError) as e:
                logger.warning(f"Error parsing render_time: {e}")
                form_data["render_time"] = None

        honeypot_triggered.send(
            sender=self.__class__, request=request, data=form_data
        )


class FakeDjangoAdminView(FakeAdminView):
    """Fake Django admin login page honeypot."""

    form_class = FakeDjangoLoginForm
    template_name = "django_honeyguard/django_admin_login.html"

    def get_error_message(self) -> str:
        """Return Django admin error message."""
        return honeyguard_settings.DJANGO_ERROR_MESSAGE


class FakeWPAdminView(FakeAdminView):
    """Fake WordPress admin login page honeypot."""

    form_class = FakeWordPressLoginForm
    template_name = "django_honeyguard/wp_admin_login.html"

    def get_error_message(self) -> str:
        """Return WordPress admin error message."""
        return honeyguard_settings.WORDPRESS_ERROR_MESSAGE
