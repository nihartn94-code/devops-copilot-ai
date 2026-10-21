from pathlib import Path
import pytest
from backend.app.services.test_analyzer_service import test_analyzer_service

def test_parse_pytest_sample():
    sample_file = Path(__file__).resolve().parent.parent.parent / "sample-data" / "tests" / "pytest-failure.txt"
    assert sample_file.exists()
    content = sample_file.read_text(encoding="utf-8")

    result = test_analyzer_service.analyze(content)
    assert result["framework"] == "pytest"
    assert result["failed"] == 2
    assert result["passed"] == 3
    assert len(result["failed_tests"]) == 2
    assert "ValidationError" in result["root_cause_summary"] or "Connection" in result["root_cause_summary"]
    assert len(result["next_steps"]) >= 2

def test_parse_jest_sample():
    sample_file = Path(__file__).resolve().parent.parent.parent / "sample-data" / "tests" / "jest-failure.txt"
    assert sample_file.exists()
    content = sample_file.read_text(encoding="utf-8")

    result = test_analyzer_service.analyze(content)
    assert result["framework"] == "jest"
    assert result["failed"] == 2
    assert len(result["failed_tests"]) >= 1
    assert "BuildStatusBadge" in result["failed_tests"][0].test_name

def test_empty_test_output():
    result = test_analyzer_service.analyze("No tests ran")
    assert result["framework"] == "generic"
