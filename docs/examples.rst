Examples
========

This page provides practical examples of using django-honeyguard in various scenarios.

Basic Setup Example
-------------------

Complete ``settings.py`` configuration:

Using Individual Views
----------------------

Instead of including all URLs, you can use individual views:

.. code-block:: python

   # urls.py
   from django.urls import path
   from django_honeyguard.views import FakeDjangoAdminView

   urlpatterns = [
       path("admin/login/", FakeDjangoAdminView.as_view(), name="fake_admin"),
       # ... your other URLs
   ]

This is useful when:

* You only need one fake login page (e.g., Django admin only)
* You want custom URL patterns
* You want different URL names
* You want to add additional middleware or decorators

Example with custom path and middleware:

.. code-block:: python

   from django.urls import path
   from django.views.decorators.cache import cache_page
   from django_honeyguard.views import FakeWPAdminView

   urlpatterns = [
       # Custom path for WordPress fake admin
       path("wp-admin/login.php", FakeWPAdminView.as_view(), name="fake_wp_login"),

       # Or with caching decorator
       path("admin/", cache_page(60 * 15)(FakeDjangoAdminView.as_view())),
   ]

Using Both Views Separately
----------------------------

Use both views with custom paths:

.. code-block:: python

   from django.urls import path
   from django_honeyguard.views import FakeDjangoAdminView, FakeWPAdminView

   urlpatterns = [
       # Custom Django admin path
       path("fake-django-admin/", FakeDjangoAdminView.as_view(), name="fake_django"),

       # Custom WordPress admin path
       path("fake-wp-admin/", FakeWPAdminView.as_view(), name="fake_wp"),
   ]

Basic Setup Example
-------------------

Complete ``settings.py`` configuration:

.. code-block:: python

   # settings.py
   INSTALLED_APPS = [
       "django.contrib.admin",
       "django.contrib.auth",
       "django.contrib.contenttypes",
       "django.contrib.sessions",
       "django_honeyguard",  # Add this
   ]

   HONEYGUARD = {
       "EMAIL_RECIPIENTS": ["security@example.com"],
       "ENABLE_CONSOLE_LOGGING": True,
       "LOG_LEVEL": "INFO",
   }

   # urls.py
   from django.urls import path, include

   urlpatterns = [
       path("admin/", admin.site.urls),
       path("", include("django_honeyguard.urls")),  # Add honeypot URLs
   ]

Custom Honeypot View Example
-----------------------------

Create a custom honeypot for a specific application:

.. code-block:: python

   # views.py
   from django.views.generic import FormView
   from django_honeyguard.views import FakeAdminView
   from django_honeyguard.forms import BaseFakeLoginForm
   from django import forms
   from django.contrib import messages

   class CustomLoginForm(BaseFakeLoginForm):
       username = forms.CharField(max_length=100, label="Email")
       password = forms.CharField(widget=forms.PasswordInput)

   class CustomHoneypotView(FakeAdminView, FormView):
       template_name = "custom_login.html"
       form_class = CustomLoginForm
       success_url = "/"

       def get_error_message(self):
           return "The email or password you entered is incorrect."

       def form_valid(self, form):
           if form.is_honeypot_triggered():
               # Honeypot already logged by parent class
               messages.error(self.request, self.get_error_message())
               return self.render_to_response(
                   self.get_context_data(form=form)
               )
           return super().form_valid(form)

   # urls.py
   urlpatterns = [
       path("account/login/", CustomHoneypotView.as_view(), name="fake_login"),
   ]

   # templates/custom_login.html
   <form method="post">
       {% csrf_token %}
       {{ form.as_p }}
       <button type="submit">Login</button>
   </form>

Signal Handler Example
----------------------

Create a custom signal handler to add additional logging:

.. code-block:: python

   # signals.py or in your app's ready() method
   from django_honeyguard.signals import honeypot_triggered
   from django.dispatch import receiver
   import logging

   logger = logging.getLogger(__name__)

   @receiver(honeypot_triggered)
   def advanced_honeypot_handler(sender, request, data, **kwargs):
       """Advanced handler with custom logic."""
       from django_honeyguard.models import HoneyGuardLog

       # Log to external service
       ip_address = data.get("ip_address")
       risk_score = data.get("risk_score", 0)

       if risk_score >= 70:
           # High-risk attack - notify external security system
           logger.warning(f"High-risk attack from {ip_address}: {risk_score}")
           # Call external API, send Slack notification, etc.

   # apps.py
   from django.apps import AppConfig

   class MyAppConfig(AppConfig):
       name = "myapp"

       def ready(self):
           import myapp.signals  # Import to register handlers

Management Command Example
---------------------------

Create a custom management command to analyze logs:

.. code-block:: python

   # management/commands/analyze_attacks.py
   from django.core.management.base import BaseCommand
   from django_honeyguard.models import HoneyGuardLog
   from django.utils import timezone
   from datetime import timedelta
   from collections import Counter

   class Command(BaseCommand):
       help = "Analyze honeypot attacks"

       def handle(self, *args, **options):
           # Last 24 hours
           since = timezone.now() - timedelta(days=1)
           logs = HoneyGuardLog.objects.filter(created_at__gte=since)

           self.stdout.write(f"Total attacks: {logs.count()}")
           self.stdout.write(f"High risk: {logs.filter(risk_score__gte=70).count()}")

           # Top IPs
           ip_counts = Counter(log.ip_address for log in logs)
           self.stdout.write("\nTop 5 attacking IPs:")
           for ip, count in ip_counts.most_common(5):
               self.stdout.write(f"  {ip}: {count}")

API Integration Example
-----------------------

Integrate with Django REST Framework:

.. code-block:: python

   # api/views.py
   from rest_framework.views import APIView
   from rest_framework.response import Response
   from rest_framework import status
   from django_honeyguard.services import HoneyGuardService

   class FakeLoginAPIView(APIView):
       """Fake login endpoint that logs honeypot attempts."""

       def post(self, request):
           data = request.data.copy()

           # Check honeypot field
           hp = data.get("hp", "").strip()
           if hp:
               # Bot detected - log it
               service = HoneyGuardService(request, data)
               service.log_trigger()

               # Return generic error
               return Response(
                   {"error": "Invalid credentials"},
                   status=status.HTTP_400_BAD_REQUEST,
               )

           # Not a bot - proceed normally
           return Response(
               {"message": "Processing login..."},
               status=status.HTTP_200_OK,
           )

   # urls.py
   from django.urls import path
   from .api.views import FakeLoginAPIView

   urlpatterns = [
       path("api/login/", FakeLoginAPIView.as_view(), name="api_login"),
   ]

Middleware Integration Example
------------------------------

Add honeypot detection to middleware:

.. code-block:: python

   # middleware.py
   from django.utils.deprecation import MiddlewareMixin
   from django_honeyguard.services import HoneyGuardService

   class HoneypotMiddleware(MiddlewareMixin):
       """Detect honeypot attempts in middleware."""

       def process_request(self, request):
           # Only check specific paths
           if request.path in ["/fake-admin/", "/fake-login/"]:
               if request.method == "POST":
                   hp = request.POST.get("hp", "").strip()
                   if hp:
                       # Bot detected
                       data = request.POST.dict()
                       service = HoneyGuardService(request, data)
                       service.log_trigger()
           return None

   # settings.py
   MIDDLEWARE = [
       # ...
       "myapp.middleware.HoneypotMiddleware",
   ]

Testing Example
---------------

Write tests for your honeypot views:

.. code-block:: python

   # tests.py
   from django.test import TestCase, Client
   from django_honeyguard.models import HoneyGuardLog

   class HoneypotTestCase(TestCase):
       def setUp(self):
           self.client = Client()

       def test_honeypot_detection(self):
           """Test that filling honeypot field logs the attempt."""
           initial_count = HoneyGuardLog.objects.count()

           # Submit form with honeypot field filled
           response = self.client.post(
               "/admin/",
               {
                   "username": "admin",
                   "password": "password",
                   "hp": "filled",  # Bot fills this
               },
           )

           # Should log the attempt
           self.assertEqual(HoneyGuardLog.objects.count(), initial_count + 1)

           log = HoneyGuardLog.objects.latest("created_at")
           self.assertTrue(log.honeypot_triggered)
           self.assertGreaterEqual(log.risk_score, 50)

       def test_human_submission(self):
           """Test that normal submission doesn't trigger."""
           initial_count = HoneyGuardLog.objects.count()

           # Submit form without honeypot field
           response = self.client.post(
               "/admin/",
               {
                   "username": "user",
                   "password": "pass",
                   "hp": "",  # Human doesn't fill this
               },
           )

           # Should not log if honeypot not triggered
           # (May still log if timing is suspicious)
           # Adjust assertion based on your needs

Log Analysis Example
--------------------

Analyze logs programmatically:

.. code-block:: python

   # analysis.py
   from django_honeyguard.models import HoneyGuardLog, TimingIssue
   from django.utils import timezone
   from datetime import timedelta
   from collections import Counter

   def analyze_attacks(days=7):
       """Analyze attacks from the last N days."""
       since = timezone.now() - timedelta(days=days)
       logs = HoneyGuardLog.objects.filter(created_at__gte=since)

       stats = {
           "total": logs.count(),
           "high_risk": logs.filter(risk_score__gte=70).count(),
           "bots": sum(1 for log in logs if log.is_bot),
           "timing_too_fast": logs.filter(timing_issue=TimingIssue.TOO_FAST).count(),
           "top_ips": Counter(log.ip_address for log in logs).most_common(10),
           "top_paths": Counter(log.path for log in logs).most_common(10),
       }

       return stats

   # Usage
   stats = analyze_attacks(30)  # Last 30 days
   print(f"Total attacks: {stats['total']}")
   print(f"High risk: {stats['high_risk']}")
   print(f"Bots detected: {stats['bots']}")

Custom Admin Action Example
---------------------------

Create custom admin actions:

.. code-block:: python

   # admin.py
   from django.contrib import admin
   from django_honeyguard.models import HoneyGuardLog
   from django.contrib import messages

   @admin.action(description="Mark selected as reviewed")
   def mark_reviewed(modeladmin, request, queryset):
       """Mark selected logs as reviewed."""
       # Add a custom field or use existing fields
       queryset.update(honeypot_triggered=False)  # Example
       messages.success(request, f"{queryset.count()} logs marked as reviewed.")

   class CustomHoneyGuardLogAdmin(admin.ModelAdmin):
       actions = [mark_reviewed]

   # Unregister default and register custom
   admin.site.unregister(HoneyGuardLog)
   admin.site.register(HoneyGuardLog, CustomHoneyGuardLogAdmin)

Email Template Customization Example
-------------------------------------

Customize email alert templates:

.. code-block:: python

   # settings.py - you can't customize the template directly,
   # but you can create a custom signal handler:

   # signals.py
   from django_honeyguard.signals import honeypot_triggered
   from django.core.mail import send_mail
   from django.dispatch import receiver

   @receiver(honeypot_triggered)
   def custom_email_handler(sender, request, data, **kwargs):
       """Send custom email alerts."""
       if data.get("risk_score", 0) >= 70:
           send_mail(
               subject="🚨 High-Risk Attack Detected",
               message=f"Attack from {data.get('ip_address')}",
               from_email="security@example.com",
               recipient_list=["admin@example.com"],
               html_message=f"""
               <h2>High-Risk Attack Detected</h2>
               <p>IP: {data.get('ip_address')}</p>
               <p>Risk Score: {data.get('risk_score')}</p>
               """,
           )

