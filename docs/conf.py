"""Sphinx configuration file for django-honeyguard documentation."""

import os
import sys
from datetime import date

# -------------------------------------------------------------
#  Django setup (for autodoc to import your models/views/etc.)
# -------------------------------------------------------------
import django

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(".."))

# Configure Django settings for autodoc
# Use test settings for documentation builds
if "DJANGO_SETTINGS_MODULE" not in os.environ:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
try:
    django.setup()
except Exception:
    # Django may already be set up or settings may not be available
    pass

# -------------------------------------------------------------
#  Project information
# -------------------------------------------------------------
project = "django-honeyguard"
copyright = f"{date.today().year}, django-honeyguard contributors"
author = "django-honeyguard contributors"

# Get version from pyproject.toml or package
try:
    from django_honeyguard import __version__

    release = __version__
    version = ".".join(release.split(".")[:2])
except ImportError:
    release = "latest"
    version = "latest"

# -------------------------------------------------------------
#  Extensions
# -------------------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
]

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True

# Autodoc settings
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": False,
    "exclude-members": "__weakref__",
}
autodoc_mock_imports = ["celery", "redis"]  # mock any external deps

# Autosummary
autosummary_generate = True

# Intersphinx
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "django": (
        "https://docs.djangoproject.com/en/stable/",
        "https://docs.djangoproject.com/en/stable/_objects/",
    ),
}

# HTML theme
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "collapse_navigation": False,
    "style_nav_header_background": "#2980B9",
}

# Static files
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# Master document
master_doc = "index"

# Exclude patterns
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Todo
todo_include_todos = True
