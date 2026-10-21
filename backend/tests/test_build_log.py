from pathlib import Path
import pytest
from backend.app.services.build_log_service import build_log_service

def test_detect_docker_tool():
    log = "#1 [internal] load build definition from Dockerfile\n#7 ERROR: process /bin/sh failed"
    tool = build_log_service.detect_tool(log)
    assert tool == "docker"

def test_detect_npm_tool():
    log = "> frontend@1.0.0 build\n> tsc -b && vite build\nerror TS2307: Cannot find module"
    tool = build_log_service.detect_tool(log)
    assert tool == "npm"

def test_extract_rust_compiler_evidence():
    log_file = Path(__file__).resolve().parent.parent.parent / "sample-data" / "logs" / "docker-build-fail.log"
    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")

    evidence = build_log_service.extract_evidence(content)
    assert "MissingRustCompilerError" in evidence.error_type
    assert "Rust" in evidence.primary_error_message
    assert evidence.exit_code == 1
    assert "cargo build" in evidence.failed_command_or_file

    hypothesis = build_log_service.generate_deterministic_hypothesis(evidence, "docker")
    assert "Rust compiler" in hypothesis.likely_root_cause
    assert len(hypothesis.prioritized_debugging_steps) >= 2
    assert "pip install --upgrade" in hypothesis.recommended_fix_code

def test_empty_or_minimal_log():
    log = "Build started...\nBuild completed with exit code 1"
    evidence = build_log_service.extract_evidence(log)
    assert evidence.exit_code == 1
    hypothesis = build_log_service.generate_deterministic_hypothesis(evidence, "generic")
    assert hypothesis.likely_root_cause != ""
