"""django-honeyguard package metadata and default app config."""

__version__ = "0.1.2"

default_app_config = "django_honeyguard.apps.HoneyGuardConfig"

__all__ = ["__version__"]


def parse_version(version: str) -> tuple[int, int, int]:
    """Parse a version string into a tuple of integers."""
    return tuple(int(part) for part in version.split("."))


VERSION = parse_version(__version__)
