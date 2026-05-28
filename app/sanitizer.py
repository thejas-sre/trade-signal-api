"""
PII Sanitizer — strips personally identifiable fields before logging.
In a regulated environment (HIPAA/GDPR), signal payloads may contain
user identifiers. This module ensures no PII reaches log output.
"""

SENSITIVE_FIELDS = ["user_id", "account_id", "email", "name", "phone"]

def sanitize_for_log(payload: dict) -> dict:
    """Remove PII-adjacent fields before logging payload."""
    return {k: v for k, v in payload.items() if k not in SENSITIVE_FIELDS}
