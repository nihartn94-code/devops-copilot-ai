import re
from typing import List, Tuple
from backend.app.models import RedactionResult

class SecretRedactionService:
    """
    Scans text for sensitive information (credentials, API keys, private keys, tokens)
    and redacts them before storing or sending to external AI models.
    """

    PATTERNS: List[Tuple[str, re.Pattern, str]] = [
        # AWS Access Key ID (standard AKIA / ASIA)
        ("AWS Access Key", re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b"), "[REDACTED_AWS_ACCESS_KEY]"),
        
        # AWS Secret Access Key (in assignments, URLs or credentials)
        ("AWS Secret Key", re.compile(r"(?i)(?:aws_secret_access_key|secret_key|aws_secret)\s*[:=]\s*['\"]?([A-Za-z0-9/+=]{40})['\"]?"), "[REDACTED_AWS_SECRET_KEY]"),
        ("AWS Secret Key Raw", re.compile(r"(?<=[=:\s])[A-Za-z0-9/+=]{40}(?=[=\s\"']|$)"), "[REDACTED_SECRET_KEY]"),

        # GitHub Personal Access Token (classic & fine-grained)
        ("GitHub Token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{36,255}\b"), "[REDACTED_GITHUB_TOKEN]"),
        ("GitHub PAT", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{82}\b"), "[REDACTED_GITHUB_PAT]"),

        # JSON Web Tokens (JWT)
        ("JWT Token", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"), "[REDACTED_JWT_TOKEN]"),

        # Private Keys (RSA, DSA, EC, OPENSSH)
        ("Private Key", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"), "[REDACTED_PRIVATE_KEY]"),

        # Database connection strings with credentials
        ("DB Connection String", re.compile(r"(?i)(?:postgres|postgresql|mysql|mongodb|redis|amqp)://(?:[^:]+):([^@]+)@"), lambda m: m.group(0).replace(m.group(1), "[REDACTED_PASSWORD]")),

        # Generic API Key / Bearer tokens in headers or logs
        ("Bearer Token", re.compile(r"(?i)bearer\s+([a-zA-Z0-9_\-\.]{20,})"), "Bearer [REDACTED_BEARER_TOKEN]"),
        ("Generic Password / Secret Assignment", re.compile(r"(?i)(?:password|passwd|secret|api_key|apikey|auth_token)\s*[:=]\s*['\"]?([^\s'\",;&]{8,})['\"]?"), lambda m: m.group(0).replace(m.group(1), "[REDACTED_SECRET]")),
    ]

    @classmethod
    def redact(cls, text: str) -> RedactionResult:
        if not text:
            return RedactionResult(clean_text="", secrets_detected=0, redactions=[])

        cleaned = text
        detected_categories: List[str] = []
        total_secrets = 0

        for category, pattern, replacement in cls.PATTERNS:
            matches = list(pattern.finditer(cleaned))
            if matches:
                total_secrets += len(matches)
                detected_categories.append(f"{category} ({len(matches)})")
                if callable(replacement):
                    cleaned = pattern.sub(replacement, cleaned)
                else:
                    cleaned = pattern.sub(replacement, cleaned)

        return RedactionResult(
            clean_text=cleaned,
            secrets_detected=total_secrets,
            redactions=detected_categories
        )

redaction_service = SecretRedactionService()
