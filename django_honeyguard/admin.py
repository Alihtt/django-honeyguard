"""Enhanced Django admin interface for HoneyGuard logs."""

import csv
from datetime import timedelta
from typing import Any

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import format_html

from .models import HoneyGuardLog


@admin.register(HoneyGuardLog)
class HoneyGuardLogAdmin(admin.ModelAdmin):
    """Enhanced admin interface for HoneyGuard logs."""

    list_display = (
        "created_at",
        "method",
        "ip_address",
        "path",
        "username_display",
        "risk_score_display",
        "timing_issue",
        "honeypot_triggered",
    )
    list_filter = (
        "created_at",
        "path",
        "method",
        "timing_issue",
        "honeypot_triggered",
    )
    search_fields = (
        "ip_address",
        "username",
        "password",
        "user_agent",
        "path",
        "referer",
    )
    date_hierarchy = "created_at"
    readonly_fields = (
        "created_at",
        "updated_at",
        "risk_score",
        "request_summary",
    )
    list_per_page = 50
    ordering = ["-created_at"]

    fieldsets = (
        (
            "Request Information",
            {
                "fields": (
                    "ip_address",
                    "path",
                    "method",
                    "created_at",
                    "updated_at",
                )
            },
        ),
        (
            "Authentication Attempt",
            {
                "fields": (
                    "username",
                    "password",
                )
            },
        ),
        (
            "Detection Flags",
            {
                "fields": (
                    "honeypot_triggered",
                    "timing_issue",
                    "elapsed_time",
                    "risk_score",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Request Metadata",
            {
                "fields": (
                    "user_agent",
                    "referer",
                    "accept_language",
                    "accept_encoding",
                    "request_summary",
                    "raw_metadata",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    actions = ["export_to_csv", "archive_old_logs"]

    @admin.display(description="Username", ordering="username")
    def username_display(self, obj: HoneyGuardLog) -> str:
        """Display username with truncation."""
        if not obj.username:
            return format_html('<span style="color: #999;">{}</span>', "—")
        return obj.username[:30] + ("..." if len(obj.username) > 30 else "")

    @admin.display(description="Risk Score", ordering="-honeypot_triggered")
    def risk_score_display(self, obj: HoneyGuardLog) -> str:
        """Display risk score with color coding."""
        score = obj.risk_score
        if score >= 70:
            color = "#dc3545"  # Red for high risk
            label = "High"
        elif score >= 40:
            color = "#ffc107"  # Yellow for medium risk
            label = "Medium"
        else:
            color = "#28a745"  # Green for low risk
            label = "Low"

        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 3px; font-weight: bold;">'
            "{} ({})"
            "</span>",
            color,
            label,
            score,
        )

    @admin.display(description="Request Summary")
    def request_summary(self, obj: HoneyGuardLog) -> str:
        """Display formatted request summary."""
        summary_parts = [
            f"<strong>IP:</strong> {obj.ip_address}",
            f"<strong>Path:</strong> {obj.path}",
            f"<strong>Method:</strong> {obj.method}",
        ]
        if obj.user_agent:
            ua_short = (
                obj.user_agent[:80] + "..."
                if len(obj.user_agent) > 80
                else obj.user_agent
            )
            summary_parts.append(f"<strong>User-Agent:</strong> {ua_short}")
        return format_html("{}", "<br>".join(summary_parts))

    @admin.action(description="Export selected logs to CSV")
    def export_to_csv(
        self, request: Any, queryset: QuerySet[HoneyGuardLog]
    ) -> HttpResponse:
        """Export selected logs to CSV format."""
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="honeyguard_logs.csv"'
        )

        writer = csv.writer(response)
        writer.writerow(
            [
                "CreatedAt",
                "IpAddress",
                "Path",
                "Method",
                "Username",
                "Password",
                "HoneypotTriggered",
                "TimingIssue",
                "ElapsedTime",
                "RiskScore",
                "UserAgent",
                "Referer",
            ]
        )

        for log in queryset:
            writer.writerow(
                [
                    log.created_at.isoformat(),
                    log.ip_address,
                    log.path,
                    log.method,
                    log.username,
                    log.password,
                    log.honeypot_triggered,
                    log.timing_issue,
                    log.elapsed_time,
                    log.risk_score,
                    log.user_agent,
                    log.referer,
                ]
            )

        return response

    @admin.action(description="Archive logs older than 90 days")
    def archive_old_logs(
        self, request: Any, queryset: QuerySet[HoneyGuardLog]
    ) -> None:
        """Archive logs older than 90 days."""
        cutoff_date = timezone.now() - timedelta(days=90)
        old_logs = queryset.filter(created_at__lt=cutoff_date)

        count = old_logs.count()
        old_logs.delete()

        self.message_user(
            request,
            f"Successfully archived {count} log(s) older than 90 days.",
        )
