from django.contrib import messages
from django.utils import timezone
from django.views.generic.edit import FormView

from .conf import settings
from .forms import FakeDjangoLoginForm, FakeWordPressLoginForm
from .signals import honeypot_triggered
from .utils import check_timing_attack, get_request_metadata


class FakeAdminView(FormView):
    """Base view for fake admin pages that act as honeypots."""

    success_url = "/"
    error_message = "Authentication failed."

    def get_error_message(self):
        """
        Get error message to display to user.

        Override in subclasses to provide specific error messages.

        Returns:
            str: Error message text
        """
        return self.error_message

    def dispatch(self, request, *args, **kwargs):
        """
        Store form render time in session for timing attack detection.

        Args:
            request: Django HttpRequest object
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Returns:
            HttpResponse: Response from parent dispatch
        """
        response = super().dispatch(request, *args, **kwargs)
        request.session["form_render_time"] = timezone.now().isoformat()
        return response

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests with optional honeypot detection.

        Args:
            request: Django HttpRequest object
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Returns:
            HttpResponse: Rendered template response
        """
        if settings.ENABLE_GET_METHOD_DETECTION:
            self._trigger_honeypot_signal(request)

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests and display error message.

        Args:
            request: Django HttpRequest object
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Returns:
            HttpResponse: Response from parent post
        """
        response = super().post(request, *args, **kwargs)
        request.session.pop("form_render_time", None)
        messages.error(request, self.get_error_message())
        return response

    def _trigger_honeypot_signal(self, request, form_data=None):
        """
        Send honeypot triggered signal with collected metadata.

        Args:
            request: Django HttpRequest object
            form_data: Dictionary of form data (optional)
        """
        metadata = get_request_metadata(request)

        if form_data:
            timing_issue, elapsed_time = self._check_timing(request)
            metadata.update(
                {
                    "username_attempted": form_data.get("username", ""),
                    "password_attempted": form_data.get("password", ""),
                    "honeypot_triggered": bool(form_data.get("hp", "")),
                    "timing_issue": timing_issue,
                    "elapsed_time": elapsed_time,
                }
            )
        else:
            metadata["honeypot_triggered"] = False

        honeypot_triggered.send(
            sender=self.__class__, request=request, data=metadata
        )

    def _check_timing(self, request):
        """
        Check for timing attacks based on form render time.

        Args:
            request: Django HttpRequest object

        Returns:
            tuple: (timing_issue, elapsed_time) or (None, None) if no render time
        """
        render_time = request.session.get("form_render_time")
        if render_time:
            return check_timing_attack(render_time)
        return None, None

    def form_valid(self, form):
        """
        Handle valid form submission (trigger honeypot).

        Args:
            form: Valid form instance

        Returns:
            HttpResponse: Re-rendered form with context
        """
        self._trigger_honeypot_signal(
            self.request,
            form_data=form.cleaned_data,
        )
        return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        """
        Handle invalid form submission (trigger honeypot).

        Args:
            form: Invalid form instance

        Returns:
            HttpResponse: Re-rendered form with context
        """
        self._trigger_honeypot_signal(self.request, form_data=form.data)
        return self.render_to_response(self.get_context_data(form=form))


class FakeDjangoAdminView(FakeAdminView):
    """Fake Django admin login page honeypot."""

    form_class = FakeDjangoLoginForm
    template_name = "django_honeyguard/django_admin_login.html"

    def get_error_message(self):
        """Get Django-specific error message from settings."""
        return settings.DJANGO_ERROR_MESSAGE


class FakeWPAdminView(FakeAdminView):
    """Fake WordPress admin login page honeypot."""

    form_class = FakeWordPressLoginForm
    template_name = "django_honeyguard/wp_admin_login.html"

    def get_error_message(self):
        """Get WordPress-specific error message from settings."""
        return settings.WORDPRESS_ERROR_MESSAGE
