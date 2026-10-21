import pytest
from backend.app.services.redaction_service import redaction_service

def test_redact_aws_access_key():
    text = "Deploying with credentials AKIAIOSFODNN7EXAMPLE to us-east-1"
    result = redaction_service.redact(text)
    assert "AKIAIOSFODNN7EXAMPLE" not in result.clean_text
    assert "[REDACTED_AWS_ACCESS_KEY]" in result.clean_text
    assert result.secrets_detected >= 1

def test_redact_github_pat():
    text = "Cloning repo with token ghp_1234567890abcdefghijklmnopqrstuvwxyzAB"
    result = redaction_service.redact(text)
    assert "ghp_" not in result.clean_text
    assert "[REDACTED_GITHUB_TOKEN]" in result.clean_text
    assert result.secrets_detected >= 1

def test_redact_jwt():
    text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    result = redaction_service.redact(text)
    assert "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c" not in result.clean_text
    assert result.secrets_detected >= 1

def test_redact_db_password():
    text = "DATABASE_URL=postgres://app_user:super_secret_p@ss123@db.prod.internal:5432/main_db"
    result = redaction_service.redact(text)
    assert "super_secret_p@ss123" not in result.clean_text
    assert "[REDACTED_PASSWORD]" in result.clean_text

def test_no_secrets_clean_text():
    text = "Standard compiler log with normal warnings: line 42 function unused."
    result = redaction_service.redact(text)
    assert result.clean_text == text
    assert result.secrets_detected == 0
