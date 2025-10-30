## django-honeyguard [![pypi version][1]][2] [![rtd][3]][4]

[![license][5]][6] [![python version][7]][2] [![django version][8]][9] [![build][10]][11]

📖 Documentation: https://django-honeyguard.readthedocs.io

HoneyGuard is a reusable Django app that provides fake admin login pages (honeypots) for Django and WordPress, logs suspicious requests, detects timing anomalies, and optionally sends alerts. Protect your real admin by wasting attackers’ time and gathering intelligence safely.


### Features

- Live timing detection (too-fast/too-slow submissions)
- Hidden honeypot field detection
- Fake login pages for Django Admin and WordPress
- Comprehensive logging with risk scores
- Pluggable signal to integrate custom handlers
- Optional email alerts and console logging
- URL include or drop-in views usage
- Strict settings validation at startup


### Preview

The package ships with templates for:
- `django_honeyguard/django_admin_login.html` (fake Django admin)
- `django_honeyguard/wp_admin_login.html` (fake WordPress admin)

Include the URLs and visit `/admin/` or `/wp-admin.php` to see the honeypots in action.


### Requirements

- Django >= 5.2.7
- Python >= 3.10


### Installation

Install from PyPI:

```bash
pip install django-honeyguard
```

Add the app to `INSTALLED_APPS`:

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "django_honeyguard",
]
```

Include the URLs (Option A), or wire views directly (Option B):

```python
# urls.py
from django.urls import include, path

urlpatterns = [
    # Option A: include both fake admin pages
    path("", include("django_honeyguard.urls")),

    # Option B: use individual views
    # from django_honeyguard.views import FakeDjangoAdminView, FakeWPAdminView
    # path("admin/", FakeDjangoAdminView.as_view()),
    # path("wp-admin.php", FakeWPAdminView.as_view()),
]
```

Run migrations (creates log table):

```bash
python manage.py migrate
```


### Settings (settings.py)

You can configure HoneyGuard via a `HONEYGUARD` dictionary or individual `HONEYGUARD_*` settings. Defaults shown below:

```python
HONEYGUARD = {
    # Email alerts
    "EMAIL_RECIPIENTS": [],
    "EMAIL_SUBJECT_PREFIX": "🚨 Honeypot Alert",
    "EMAIL_FROM": None,              # Uses Django DEFAULT_FROM_EMAIL if None
    "EMAIL_FAIL_SILENTLY": True,     # Do not crash on email errors

    # Timing detection (seconds)
    "TIMING_TOO_FAST_THRESHOLD": 2.0,
    "TIMING_TOO_SLOW_THRESHOLD": 600.0,

    # Logging
    "ENABLE_CONSOLE_LOGGING": True,
    "LOG_LEVEL": "WARNING",        # DEBUG, INFO, WARNING, ERROR, CRITICAL

    # Detection behavior
    "ENABLE_GET_METHOD_DETECTION": False,  # Detect on GET as well as POST

    # Field limits
    "MAX_USERNAME_LENGTH": 150,
    "MAX_PASSWORD_LENGTH": 128,
    "WORDPRESS_USERNAME_MAX_LENGTH": 60,
    "WORDPRESS_PASSWORD_MAX_LENGTH": 255,

    # Error messages (shown on fake pages)
    "DJANGO_ERROR_MESSAGE": (
        "Please enter a correct username and password. Note that both fields"
        " may be case-sensitive."
    ),
    "WORDPRESS_ERROR_MESSAGE": (
        "<strong>Error:</strong> The password you entered for the username is incorrect."
    ),
}
```


### Usage

- Visit `/admin/` for the fake Django admin login page
- Visit `/wp-admin.php` for the fake WordPress login page
- Submissions and suspicious GETs will be logged via the `honeypot_triggered` signal

Listen to the `honeypot_triggered` signal to add custom behaviors:

```python
from django_honeyguard.signals import honeypot_triggered
from django.dispatch import receiver

@receiver(honeypot_triggered)
def my_handler(sender, request, data, **kwargs):
    # data contains ip_address, path, username, timing info, risk_score, etc.
    pass
```


### Documentation

Complete documentation is available at: https://django-honeyguard.readthedocs.io/

Running the docs locally:

```bash
git clone https://github.com/alihtt/django-honeyguard.git
cd django-honeyguard
python -m venv .venv && source .venv/bin/activate
pip install -r docs/requirements.txt
cd docs && make html
# open _build/html/index.html in your browser
```


### Notes

- This package does not replace Django’s real authentication; it provides decoy pages and logging.
- Always secure your real admin at a non-obvious URL and behind proper authentication and rate limiting.


[1]: https://img.shields.io/pypi/v/django-honeyguard.svg
[2]: https://pypi.org/project/django-honeyguard/
[3]: https://readthedocs.org/projects/django-honeyguard/badge/?version=latest
[4]: https://django-honeyguard.readthedocs.io/en/latest/
[5]: https://img.shields.io/badge/license-MIT-blue.svg
[6]: https://github.com/alihtt/django-honeyguard/blob/main/LICENSE
[7]: https://img.shields.io/pypi/pyversions/django-honeyguard.svg
[8]: https://img.shields.io/badge/Django-%3E%3D%205.2.7-green.svg
[9]: https://www.djangoproject.com
[10]: https://img.shields.io/github/actions/workflow/status/alihtt/django-honeyguard/tests.yml?branch=main
[11]: https://github.com/alihtt/django-honeyguard/actions
