# Makefile for django-honeyguard documentation

.PHONY: help docs html clean

help:
	@echo "Available commands:"
	@echo "  make docs      - Build Sphinx documentation"
	@echo "  make html       - Build HTML documentation (same as docs)"
	@echo "  make clean      - Clean build files"

docs html:
	@echo "Building documentation..."
	@cd docs && sphinx-build -b html . _build/html
	@echo "Documentation built in docs/_build/html/"

clean:
	@echo "Cleaning build files..."
	@rm -rf docs/_build
	@rm -rf docs/_static/.doctrees
	@echo "Clean complete."

