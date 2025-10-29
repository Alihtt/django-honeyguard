"""Constants for HoneyGuard logging and email formatting."""

# Console log format string
CONSOLE_LOG_FORMAT = (
    "Honeypot triggered: "
    "IP={ip_address}, "
    "Path={path}, "
    "Method={method}, "
    "CreatedAt={created_at}, "
    "Username={username}, "
    "Password={password}, "
    "UserAgent={user_agent}, "
    "Referer={referer}, "
    "AcceptLanguage={accept_language}, "
    "AcceptEncoding={accept_encoding}, "
    "ElapsedTime={elapsed_time}s, "
    "TimingIssue={timing_issue}, "
    "HoneypotTriggered={honeypot_triggered}, "
    "RawMetadata={raw_metadata}"
)

# Email alert body template
EMAIL_ALERT_BODY = """🚨 Honeypot Alert - {path}

=== Request Details ===
IP Address: {ip_address}
Path: {path}
Method: {method}
CreatedAt: {created_at}

=== Authentication Attempt ===
Username: {username}
Password: {password}

=== Detection Flags ===
Honeypot Field Triggered: {honeypot_triggered}
Timing Issue: {timing_issue}
Submission Time: {elapsed_time:.2f} seconds

=== Browser & Environment ===
User Agent: {user_agent}
Referer: {referer}
Accept-Language: {accept_language}
Accept-Encoding: {accept_encoding}

=== Full Metadata ===
{raw_metadata}
"""
