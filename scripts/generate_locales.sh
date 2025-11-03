#!/bin/bash
# Script to generate locale files for django-honeyguard
# Usage: ./generate_locales.sh

echo "Generating translation files for django-honeyguard..."

# Popular language codes
LANGUAGES=(
    "ar"      # Arabic
    "be"      # Belarusian
    "bg"      # Bulgarian
    "cs"      # Czech
    "da"      # Danish
    "de"      # German
    "el"      # Greek
    "es"      # Spanish
    "fa"      # Persian (Farsi)
    "fi"      # Finnish
    "fr"      # French
    "it"      # Italian
    "ja"      # Japanese
    "ko"      # Korean
    "nl"      # Dutch
    "pl"      # Polish
    "ro"      # Romanian
    "ru"      # Russian
    "sk"      # Slovak
    "sv"      # Swedish
    "tr"      # Turkish
    "uk"      # Ukrainian
    "vi"      # Vietnamese
    "zh"      # Chinese
    "hi"      # Hindi
    "id"      # Indonesian
)

# Change to the django_honeyguard directory
cd "$(dirname "$0")/django_honeyguard" || exit 1

# Create locale directory if it doesn't exist
mkdir -p locale

# Generate message files for each language
for lang in "${LANGUAGES[@]}"; do
    echo "Generating locale for: $lang"
    django-admin makemessages -l "$lang" --no-obsolete
done

echo ""
echo "✓ Translation files generated successfully!"
echo ""
echo "Next steps:"
echo "1. Edit the .po files in django_honeyguard/locale/*/LC_MESSAGES/django.po"
echo "2. Translate the msgid strings to msgstr"
echo "3. Run: django-admin compilemessages (from django_honeyguard directory)"
echo "4. Test your translations in Django admin"
echo ""
echo "For more information, see LOCALIZATION.md"

