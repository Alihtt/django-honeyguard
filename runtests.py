"""
Simple test runner to invoke pytest for django-honeyguard.

Usage:
    python runtests.py
    python runtests.py tests/test_models.py -k HoneyGuardLog
"""

from __future__ import annotations

import os
import sys


def main() -> int:
    # Ensure project root on sys.path
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, here)

    # Default Django settings for tests if not provided
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

    try:
        import pytest  # type: ignore
    except Exception as exc:  # pragma: no cover
        print(
            "pytest is required to run tests. Install with: pip install -e '.[dev]'",
            file=sys.stderr,
        )
        print(f"Import error: {exc}", file=sys.stderr)
        return 1

    # Pass through any CLI args to pytest
    return pytest.main(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
