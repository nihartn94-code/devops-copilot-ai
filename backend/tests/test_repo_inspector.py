from pathlib import Path
import pytest
from backend.app.services.repo_service import repo_inspector

def test_system_directory_denial():
    with pytest.raises(PermissionError):
        repo_inspector.validate_and_resolve_path("C:\\Windows")

def test_non_existent_directory():
    with pytest.raises(FileNotFoundError):
        repo_inspector.validate_and_resolve_path("C:\\non_existent_dir_12345")

def test_sample_repo_inspection():
    sample_dir = Path(__file__).resolve().parent.parent.parent / "sample-data" / "sample-repo"
    assert sample_dir.exists()

    resolved = repo_inspector.validate_and_resolve_path(str(sample_dir))
    data = repo_inspector.inspect(resolved)

    assert "JavaScript" in data["languages_detected"]
    assert "package.json" in data["config_files_found"]
    assert "Express" in data["frameworks_detected"]
    assert data["git_status"]["is_git_repo"] is True
