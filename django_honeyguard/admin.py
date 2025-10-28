from django.contrib import admin

from .models import HoneyGuardLog


@admin.register(HoneyGuardLog)
class HoneyGuardLogAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "request_method",
        "ip_address",
        "path",
        "username_attempted",
        "password_attempted",
        "risk_score",
        "user_agent",
    )
    list_filter = ("timestamp", "path", "request_method", "timing_issue")
    search_fields = (
        "ip_address",
        "username_attempted",
        "password_attempted",
        "user_agent",
        "path",
    )
    date_hierarchy = "timestamp"
