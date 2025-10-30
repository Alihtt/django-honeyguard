# Makefile for django-honeyguard documentation

.PHONY: help html clean

help:
	@echo "Available commands:"
	@echo "  make html       - Build HTML documentation (same as docs)"
	@echo "  make clean      - Clean build files"

html:
	@echo "Building documentation..."
	@sphinx-build -b html . _build/html
	@echo "Documentation built in _build/html/"

clean:
	@echo "Cleaning build files..."
	@rm -rf _build
	@rm -rf ./_static/.doctrees
	@echo "Clean complete."

