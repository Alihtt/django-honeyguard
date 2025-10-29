.. django-honeyguard documentation master file

==================================
django-honeyguard Documentation
==================================

**django-honeyguard** is a Django application that provides honeypot security mechanisms to detect and log bot attacks on fake admin login pages. It implements timing-based attack detection, hidden field honeypots, and comprehensive logging.

Features
========

* **Hidden Honeypot Fields**: Detect bots by monitoring hidden form fields that humans shouldn't fill
* **Timing Attack Detection**: Identify suspiciously fast or slow form submissions
* **Multiple CMS Support**: Fake login pages for Django admin and WordPress
* **Comprehensive Logging**: Database, console, and email logging of all attacks
* **Risk Assessment**: Automatic calculation of risk scores for each attack
* **Admin Interface**: Enhanced Django admin with filters, actions, and analytics
* **Configuration Validation**: Early detection of configuration errors at startup

Quick Start
===========

1. Install the package:

.. code-block:: bash

   pip install django-honeyguard

2. Add to your ``INSTALLED_APPS``:

.. code-block:: python

   INSTALLED_APPS = [
       # ...
       "django_honeyguard",
   ]

3. Configure in your ``settings.py``:

.. code-block:: python

   HONEYGUARD = {
       "EMAIL_RECIPIENTS": ["admin@example.com"],
       "ENABLE_CONSOLE_LOGGING": True,
   }

4. Include URLs (option A) or use views directly (option B):

.. code-block:: python

   # Option A: Include all URLs
   urlpatterns = [
       path("", include("django_honeyguard.urls")),
   ]

   # Option B: Use individual views directly
   from django_honeyguard.views import FakeDjangoAdminView
   urlpatterns = [
       path("admin/", FakeDjangoAdminView.as_view()),
   ]

5. Run migrations:

.. code-block:: bash

   python manage.py migrate

Contents
========

.. toctree::
   :maxdepth: 2

   installation
   configuration
   examples
   api
   contributing
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

