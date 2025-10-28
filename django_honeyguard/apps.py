from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HoneyGuardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_honeyguard"
    verbose_name = _("HoneyGuard")

    def ready(self):
        from . import handlers  # noqa
