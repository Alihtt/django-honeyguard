Configuration
==============

django-honeyguard can be configured using either a dictionary-style configuration or individual settings. All settings are optional and have sensible defaults.

Configuration Methods
---------------------

Method 1: Dictionary Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The recommended approach is to use a ``HONEYGUARD`` dictionary in your ``settings.py``:

.. code-block:: python

   HONEYGUARD = {
       "EMAIL_RECIPIENTS": ["admin@example.com"],
       "EMAIL_SUBJECT_PREFIX": "🚨 Honeypot Alert",
       "ENABLE_CONSOLE_LOGGING": True,
       "LOG_LEVEL": "INFO",
   }

Method 2: Individual Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can also use individual ``HONEYGUARD_*`` settings:

.. code-block:: python

   HONEYGUARD_EMAIL_RECIPIENTS = ["admin@example.com"]
   HONEYGUARD_EMAIL_SUBJECT_PREFIX = "🚨 Honeypot Alert"
   HONEYGUARD_ENABLE_CONSOLE_LOGGING = True

.. note::

   If both methods are used, the dictionary configuration takes priority over individual settings.

Available Settings
------------------

Email Configuration
~~~~~~~~~~~~~~~~~~~~

.. py:data:: EMAIL_RECIPIENTS

   **Type**: ``List[str]``
   **Default**: ``[]``
   **Description**: List of email addresses to receive honeypot alerts.

   .. code-block:: python

      HONEYGUARD = {
          "EMAIL_RECIPIENTS": [
              "admin@example.com",
              "security@example.com",
          ],
      }

   If empty, email alerts will be disabled.

.. py:data:: EMAIL_SUBJECT_PREFIX

   **Type**: ``str``
   **Default**: ``"🚨 Honeypot Alert"``
   **Description**: Prefix for email alert subject lines.

   .. code-block:: python

      HONEYGUARD = {
          "EMAIL_SUBJECT_PREFIX": "[Security Alert]",
      }

.. py:data:: EMAIL_FROM

   **Type**: ``str | None``
   **Default**: ``None``
   **Description**: From address for email alerts. If ``None``, uses Django's ``DEFAULT_FROM_EMAIL``.

   .. code-block:: python

      HONEYGUARD = {
          "EMAIL_FROM": "security@example.com",
      }

.. py:data:: EMAIL_FAIL_SILENTLY

   **Type**: ``bool``
   **Default**: ``True``
   **Description**: If ``True``, email sending errors won't raise exceptions.

Logging Configuration
~~~~~~~~~~~~~~~~~~~~~

.. py:data:: ENABLE_CONSOLE_LOGGING

   **Type**: ``bool``
   **Default**: ``True``
   **Description**: Enable console logging of honeypot triggers.

   .. code-block:: python

      HONEYGUARD = {
          "ENABLE_CONSOLE_LOGGING": False,  # Disable console logs
      }

.. py:data:: LOG_LEVEL

   **Type**: ``str``
   **Default**: ``"INFO"``
   **Valid Values**: ``"DEBUG"``, ``"INFO"``, ``"WARNING"``, ``"ERROR"``
   **Description**: Logging level for console output.

   .. code-block:: python

      HONEYGUARD = {
          "LOG_LEVEL": "WARNING",  # Only log warnings and errors
      }

Timing Attack Detection
~~~~~~~~~~~~~~~~~~~~~~~

.. py:data:: TIMING_TOO_FAST_THRESHOLD

   **Type**: ``float``
   **Default**: ``2.0``
   **Description**: Minimum time in seconds considered normal for form submission. Submissions faster than this are flagged.

   .. code-block:: python

      HONEYGUARD = {
          "TIMING_TOO_FAST_THRESHOLD": 3.0,  # Require at least 3 seconds
      }

.. py:data:: TIMING_TOO_SLOW_THRESHOLD

   **Type**: ``float``
   **Default**: ``600.0``
   **Description**: Maximum time in seconds before form submission is considered suspiciously slow.

   .. code-block:: python

      HONEYGUARD = {
          "TIMING_TOO_SLOW_THRESHOLD": 1200.0,  # 20 minutes
      }

GET Method Detection
~~~~~~~~~~~~~~~~~~~~

.. py:data:: ENABLE_GET_METHOD_DETECTION

   **Type**: ``bool``
   **Default**: ``True``
   **Description**: If ``True``, GET requests to admin URLs trigger honeypot detection.

   .. code-block:: python

      HONEYGUARD = {
          "ENABLE_GET_METHOD_DETECTION": False,  # Only detect POST requests
      }

Form Field Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

.. py:data:: MAX_USERNAME_LENGTH

   **Type**: ``int``
   **Default**: ``150``
   **Description**: Maximum length for Django admin username fields.

.. py:data:: MAX_PASSWORD_LENGTH

   **Type**: ``int``
   **Default**: ``128``
   **Description**: Maximum length for Django admin password fields.

.. py:data:: WORDPRESS_USERNAME_MAX_LENGTH

   **Type**: ``int``
   **Default**: ``60``
   **Description**: Maximum length for WordPress username fields.

.. py:data:: WORDPRESS_PASSWORD_MAX_LENGTH

   **Type**: ``int``
   **Default**: ``64``
   **Description**: Maximum length for WordPress password fields.

Error Messages
~~~~~~~~~~~~~~

.. py:data:: DJANGO_ERROR_MESSAGE

   **Type**: ``str``
   **Default**: ``"Please enter a correct username and password."``
   **Description**: Error message shown when Django admin honeypot is triggered.

   .. code-block:: python

      HONEYGUARD = {
          "DJANGO_ERROR_MESSAGE": "Invalid credentials.",
      }

.. py:data:: WORDPRESS_ERROR_MESSAGE

   **Type**: ``str``
   **Default**: ``"Invalid username or password."``
   **Description**: Error message shown when WordPress admin honeypot is triggered.

Configuration Validation
------------------------

django-honeyguard validates all configuration settings at application startup. Invalid settings will raise ``django.core.exceptions.ImproperlyConfigured`` with a clear error message.

Example errors and fixes:

**Invalid email recipient:**

.. code-block:: python

   HONEYGUARD = {
       "EMAIL_RECIPIENTS": "not-a-list",  # ❌ Wrong: should be a list
   }

   # ✅ Correct:
   HONEYGUARD = {
       "EMAIL_RECIPIENTS": ["admin@example.com"],
   }

**Invalid timing threshold:**

.. code-block:: python

   HONEYGUARD = {
       "TIMING_TOO_FAST_THRESHOLD": -5,  # ❌ Wrong: must be positive
   }

   # ✅ Correct:
   HONEYGUARD = {
       "TIMING_TOO_FAST_THRESHOLD": 2.0,
   }

**Invalid log level:**

.. code-block:: python

   HONEYGUARD = {
       "LOG_LEVEL": "VERBOSE",  # ❌ Wrong: not a valid level
   }

   # ✅ Correct:
   HONEYGUARD = {
       "LOG_LEVEL": "DEBUG",
   }

Complete Example
----------------

Here's a complete configuration example for a production environment:

.. code-block:: python

   # settings.py
   HONEYGUARD = {
       # Email alerts
       "EMAIL_RECIPIENTS": [
           "security@example.com",
           "admin@example.com",
       ],
       "EMAIL_SUBJECT_PREFIX": "[Honeypot Alert]",
       "EMAIL_FROM": "security@example.com",
       "EMAIL_FAIL_SILENTLY": False,  # Raise on email errors in production

       # Logging
       "ENABLE_CONSOLE_LOGGING": True,
       "LOG_LEVEL": "WARNING",

       # Timing detection
       "TIMING_TOO_FAST_THRESHOLD": 2.0,
       "TIMING_TOO_SLOW_THRESHOLD": 600.0,

       # Detection options
       "ENABLE_GET_METHOD_DETECTION": True,

       # Custom messages
       "DJANGO_ERROR_MESSAGE": "Invalid credentials.",
       "WORDPRESS_ERROR_MESSAGE": "Invalid username or password.",
   }

   # Ensure Django can send emails
   EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
   EMAIL_HOST = "smtp.example.com"
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = "security@example.com"
   EMAIL_HOST_PASSWORD = "your-password"
   DEFAULT_FROM_EMAIL = "security@example.com"

