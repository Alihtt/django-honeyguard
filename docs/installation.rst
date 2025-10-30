Installation
=============

django-honeyguard can be installed using pip or by cloning the repository.

Using pip
---------

The recommended way to install django-honeyguard is using pip:

.. code-block:: bash

   pip install django-honeyguard

Or to install from the latest source:

.. code-block:: bash

   pip install git+https://github.com/alihtt/django-honeyguard.git

For development, install with extra dependencies:

.. code-block:: bash

   pip install -e ".[dev]"

Dependencies
------------

django-honeyguard requires:

* **Python**: 3.10 or higher
* **Django**: 5.2.7 or higher

All other dependencies are listed in ``pyproject.toml``.

Django Configuration
--------------------

1. **Add to INSTALLED_APPS**

   Add ``django_honeyguard`` to your ``INSTALLED_APPS`` in ``settings.py``:

   .. code-block:: python

      INSTALLED_APPS = [
          "django.contrib.admin",
          "django.contrib.auth",
          # ...
          "django_honeyguard",
      ]

2. **Run Migrations**

   Run Django migrations to create the necessary database tables:

   .. code-block:: bash

      python manage.py migrate django_honeyguard

   This creates the ``HoneyGuardLog`` model table for storing attack logs.

3. **Include URLs** (Optional)

   **Option A: Include all URLs**

   If you want to use the default fake admin URLs, include them in your ``urls.py``:

   .. code-block:: python

      from django.urls import path, include

      urlpatterns = [
          # ... your other URLs
          path("", include("django_honeyguard.urls")),
      ]

   This adds the following URLs:

   * ``/admin/`` - Fake Django admin login
   * ``/wp-admin.php`` - Fake WordPress admin login

   **Option B: Import views directly**

   If you only need specific fake login pages, you can import and use individual views:

   .. code-block:: python

      from django.urls import path
      from django_honeyguard.views import FakeDjangoAdminView, FakeWPAdminView

      urlpatterns = [
          # ... your other URLs
          path("fake-admin/", FakeDjangoAdminView.as_view(), name="fake_django_admin"),
          # Or only WordPress:
          # path("wp-login/", FakeWPAdminView.as_view(), name="fake_wp_admin"),
      ]

   This approach gives you more control over:

   * Which URLs to expose
   * URL path names
   * Custom URL patterns (e.g., ``path("admin/login/", ...)``)

4. **Configure Settings**

   See :doc:`configuration` for detailed configuration options.

Verification
------------

To verify the installation:

1. Check that the app is properly configured:

   .. code-block:: python

      python manage.py check

2. Verify the admin is registered:

   .. code-block:: bash

      python manage.py shell

   .. code-block:: python

      >>> from django.contrib import admin
      >>> from django_honeyguard.models import HoneyGuardLog
      >>> HoneyGuardLog in admin.site._registry
      True

3. Test the URLs are accessible:

   Visit ``http://localhost:8000/admin/`` in your browser (if URLs are included).

Next Steps
----------

* Read the :doc:`configuration` guide to set up email alerts and logging
* Check :doc:`examples` for integration patterns and usage examples

