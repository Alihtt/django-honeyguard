API Reference
=============

This page documents the complete API for django-honeyguard.

Models
------

.. automodule:: django_honeyguard.models
   :members:
   :undoc-members:
   :show-inheritance:

Views
-----

.. automodule:: django_honeyguard.views
   :members:
   :undoc-members:
   :show-inheritance:

Forms
-----

.. automodule:: django_honeyguard.forms
   :members:
   :undoc-members:
   :show-inheritance:

Services
--------

.. automodule:: django_honeyguard.services
   :members:
   :undoc-members:
   :show-inheritance:

Signals
-------

.. automodule:: django_honeyguard.signals
   :members:
   :undoc-members:

.. _signal-honeypot-triggered:

``honeypot_triggered`` Signal
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Signal emitted when honeypot is triggered.

**Arguments:**

* ``sender`` - The sender class
* ``request`` - Django HttpRequest object
* ``data`` - Dictionary with attack data including:
  * ``ip_address``
  * ``path``
  * ``username``
  * ``password`` (sanitized)
  * ``honeypot_triggered``
  * ``timing_issue``
  * ``elapsed_time``
  * ``risk_score``

**Example:**

.. code-block:: python

   from django_honeyguard.signals import honeypot_triggered
   from django.dispatch import receiver

   @receiver(honeypot_triggered)
   def my_handler(sender, request, data, **kwargs):
       print(f"Attack from {data['ip_address']}")

Utilities
---------

.. automodule:: django_honeyguard.utils
   :members:
   :undoc-members:

Configuration
-------------

.. automodule:: django_honeyguard.conf
   :members:
   :undoc-members:

Admin
-----

.. automodule:: django_honeyguard.admin
   :members:
   :undoc-members:

Loggers
-------

.. automodule:: django_honeyguard.loggers
   :members:
   :undoc-members:

