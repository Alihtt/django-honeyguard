Contributing
============

Thank you for your interest in contributing to django-honeyguard!

Getting Started
---------------

1. **Fork the repository** on GitHub

2. **Clone your fork:**

   .. code-block:: bash

      git clone https://github.com/yourusername/django-honeyguard.git
      cd django-honeyguard

3. **Create a virtual environment:**

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate

4. **Install dependencies:**

   .. code-block:: bash

      pip install -e ".[dev]"

5. **Run tests:**

   .. code-block:: bash

      pytest

Development Setup
-----------------

Install development dependencies:

.. code-block:: bash

   pip install -e ".[dev]"

This installs:

* Django and required dependencies
* pytest and pytest-django for testing
* Coverage tools
* Linting tools

Running Tests
-------------

Run all tests:

.. code-block:: bash

   pytest

Run with coverage:

.. code-block:: bash

   pytest --cov=django_honeyguard --cov-report=html

Run specific test file:

.. code-block:: bash

   pytest tests/test_models.py

Run specific test:

.. code-block:: bash

   pytest tests/test_models.py::TestHoneyGuardLogModel::test_risk_score_calculation

Code Style
----------

We follow PEP 8 style guidelines. Use black for formatting:

.. code-block:: bash

   black django_honeyguard tests

And isort for import sorting:

.. code-block:: bash

   isort django_honeyguard tests

Check with flake8:

.. code-block:: bash

   flake8 django_honeyguard tests

Type Hints
----------

We use type hints throughout the codebase. Always add type hints to:

* Function parameters
* Return values
* Class attributes

Example:

.. code-block:: python

   def process_request(request: HttpRequest, data: Dict[str, Any]) -> HttpResponse:
       """Process honeypot request."""
       pass

Writing Tests
-------------

* All new features must include tests
* Aim for at least 95% code coverage
* Use descriptive test names
* Group related tests in classes
* Use fixtures from ``conftest.py`` when available

Example:

.. code-block:: python

   def test_honeypot_detection_with_custom_field(self, sample_request):
       """Test that custom honeypot field is detected."""
       data = {"custom_hp": "filled"}
       service = HoneyGuardService(sample_request, data)
       assert service.data["honeypot_triggered"] is True

Documentation
--------------

* Update relevant documentation files
* Add docstrings to all public functions and classes
* Use Google-style docstrings
* Update examples if behavior changes

Commit Messages
---------------

Follow conventional commits:

* ``feat:`` - New feature
* ``fix:`` - Bug fix
* ``docs:`` - Documentation changes
* ``test:`` - Test additions/changes
* ``refactor:`` - Code refactoring
* ``style:`` - Code style changes
* ``chore:`` - Maintenance tasks

Examples:

.. code-block:: bash

   git commit -m "feat: Add custom error message configuration"
   git commit -m "fix: Handle None request in signal handler"
   git commit -m "docs: Update installation guide"

Pull Request Process
--------------------

1. **Create a feature branch:**

   .. code-block:: bash

      git checkout -b feature/my-new-feature

2. **Make your changes** and commit them

3. **Push to your fork:**

   .. code-block:: bash

      git push origin feature/my-new-feature

4. **Open a Pull Request** on GitHub

5. **Ensure all checks pass:**

   * Tests pass
   * Code coverage is maintained
   * Linting passes
   * Documentation is updated

6. **Address review feedback** if requested

Pull Request Checklist
----------------------

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Type hints added
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Coverage maintained
- [ ] CHANGELOG updated (if applicable)

Reporting Issues
----------------

When reporting bugs, please include:

* Django version
* Python version
* django-honeyguard version
* Steps to reproduce
* Expected behavior
* Actual behavior
* Error messages/tracebacks

Feature Requests
----------------

For feature requests:

* Describe the use case
* Explain why it would be useful
* Provide examples if possible

License
-------

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

Questions?
----------

Feel free to open an issue or discussion on GitHub for any questions.

