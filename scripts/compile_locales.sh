#!/bin/bash
# Script to compile locale files for django-honeyguard
# Usage: ./compile_locales.sh

echo "Compiling translation files for django-honeyguard..."

# Change to the django_honeyguard directory
cd "$(dirname "$0")/django_honeyguard" || exit 1

# Check if locale directory exists
if [ ! -d "locale" ]; then
    echo "Error: locale directory not found!"
    echo "Please run ./generate_locales.sh first"
    exit 1
fi

# Compile all message files
django-admin compilemessages

echo ""
echo "✓ Translation files compiled successfully!"
echo ""
echo "The .mo files have been generated and are ready for use."
echo "You can now test your translations in Django admin."

