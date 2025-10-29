from django.contrib import admin

from .models import HoneyGuardLog


@admin.register(HoneyGuardLog)
class HoneyGuardLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "method",
        "ip_address",
        "path",
        "username",
        "password",
        "risk_score",
        "user_agent",
    )
    list_filter = ("created_at", "path", "method", "timing_issue")
    search_fields = ("ip_address", "username", "password", "user_agent", "path")
    date_hierarchy = "created_at"
