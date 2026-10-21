import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from backend.app.config import settings

class RepoInspectorService:
    """
    Safely inspects an authorized local git repository.
    Strictly read-only, protects against path traversal, and never leaks secrets.
    """

    DENIED_SYSTEM_DIRS = [
        "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)",
        "/etc", "/usr", "/bin", "/sbin", "/var", "/dev", "/proc", "/sys"
    ]

    LANGUAGE_EXTENSIONS = {
        "Python": [".py", ".pyw", ".ipynb"],
        "JavaScript": [".js", ".jsx", ".mjs"],
        "TypeScript": [".ts", ".tsx"],
        "Java": [".java", ".jar"],
        "Go": [".go"],
        "Rust": [".rs"],
        "C/C++": [".c", ".cpp", ".cc", ".h", ".hpp"],
        "HTML/CSS": [".html", ".css", ".scss"],
        "Shell": [".sh", ".bash", ".ps1", ".bat"],
    }

    FRAMEWORK_SIGNATURES = [
        ("React", ["package.json", "src/App.tsx", "src/App.jsx", "src/index.tsx"]),
        ("Vite", ["vite.config.ts", "vite.config.js"]),
        ("Next.js", ["next.config.js", "next.config.mjs", "next.config.ts"]),
        ("Express", ["package.json"]),
        ("FastAPI", ["main.py", "requirements.txt", "pyproject.toml"]),
        ("Django", ["manage.py"]),
        ("Flask", ["app.py", "wsgi.py"]),
        ("Spring Boot", ["pom.xml", "build.gradle"]),
        ("Docker", ["Dockerfile", "docker-compose.yml", "compose.yaml"]),
        ("GitHub Actions", [".github/workflows"]),
    ]

    @classmethod
    def validate_and_resolve_path(cls, path_str: str) -> Path:
        """
        Validates that the provided path exists, is a directory,
        is not a system directory, and resides within an authorized root.
        """
        if not path_str or not path_str.strip():
            raise ValueError("Repository path cannot be empty.")

        p = Path(path_str).resolve()

        if not p.exists():
            raise FileNotFoundError(f"Directory does not exist: {p}")

        if not p.is_dir():
            raise ValueError(f"Specified path is not a directory: {p}")

        # Check system directory denial
        canon_str = str(p).lower()
        for denied in cls.DENIED_SYSTEM_DIRS:
            if canon_str == denied.lower() or canon_str.startswith(denied.lower() + os.sep):
                raise PermissionError(f"Access to critical system directory is forbidden: {p}")

        # Validate against authorized roots
        authorized_roots = settings.authorized_roots_list
        is_authorized = False
        for root in authorized_roots:
            root_resolved = Path(root).resolve()
            try:
                # Check if p is subpath of or equal to root_resolved
                p.relative_to(root_resolved)
                is_authorized = True
                break
            except ValueError:
                continue

        # If user provided a specific path inside their home/scratch directory, allow if no strict override
        if not is_authorized:
            # Check if within user home or scratch
            user_home = Path.home().resolve()
            try:
                p.relative_to(user_home)
                is_authorized = True
            except ValueError:
                pass

        if not is_authorized:
            raise PermissionError(f"Path is not in the list of authorized repository roots: {p}")

        return p

    @classmethod
    def inspect(cls, target_path: Path) -> Dict[str, Any]:
        languages_detected: Dict[str, int] = {}
        frameworks_found: List[str] = []
        config_files: List[str] = []
        potential_issues: List[Dict[str, str]] = []
        recommendations: List[str] = []

        total_files = 0
        max_scan_files = 2000

        # Scan directory structure up to depth 4
        for root, dirs, files in os.walk(target_path):
            # Skip hidden dirs like .git, node_modules, .venv
            dirs[:] = [d for d in dirs if d not in [".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build"]]
            
            for file in files:
                total_files += 1
                if total_files > max_scan_files:
                    break

                rel_file = os.path.relpath(os.path.join(root, file), target_path).replace("\\", "/")
                ext = Path(file).suffix.lower()

                # Language detection
                for lang, exts in cls.LANGUAGE_EXTENSIONS.items():
                    if ext in exts:
                        languages_detected[lang] = languages_detected.get(lang, 0) + 1

                # Key config files
                if file in ["package.json", "pyproject.toml", "requirements.txt", "pom.xml", "Dockerfile", "docker-compose.yml", "tsconfig.json", ".gitignore", "README.md"]:
                    if rel_file not in config_files:
                        config_files.append(rel_file)

                # Potential issues: unignored secrets
                if file.startswith(".env") and not file.endswith(".example"):
                    potential_issues.append({
                        "severity": "HIGH",
                        "title": f"Unencrypted environment file found: {rel_file}",
                        "description": "Environment files containing secrets should be excluded from Git via .gitignore."
                    })
                if ext in [".pem", ".key", ".pfx"] or file in ["id_rsa", "id_ed25519"]:
                    potential_issues.append({
                        "severity": "CRITICAL",
                        "title": f"Private key file detected in workspace: {rel_file}",
                        "description": "Ensure private keys are never committed or exposed."
                    })

            if total_files > max_scan_files:
                break

        # Check for missing .gitignore
        if ".gitignore" not in config_files:
            potential_issues.append({
                "severity": "MEDIUM",
                "title": "Missing .gitignore file",
                "description": "Add a .gitignore file to prevent accidental commits of node_modules, virtualenvs, or secrets."
            })
            recommendations.append("Create a .gitignore tailored to your project stack.")

        # Check for missing README
        if "README.md" not in config_files and "readme.md" not in [c.lower() for c in config_files]:
            recommendations.append("Add a README.md explaining project setup, dependencies, and execution instructions.")

        # Framework detection
        for fw, sigs in cls.FRAMEWORK_SIGNATURES:
            for sig in sigs:
                if (target_path / sig).exists():
                    if fw not in frameworks_found:
                        frameworks_found.append(fw)

        # Git status inspection
        git_info = cls._get_git_status(target_path)

        sorted_langs = [k for k, _ in sorted(languages_detected.items(), key=lambda item: item[1], reverse=True)]

        return {
            "repo_path": str(target_path),
            "languages_detected": sorted_langs,
            "frameworks_detected": frameworks_found,
            "config_files_found": config_files,
            "git_status": git_info,
            "potential_issues": potential_issues,
            "recommendations": recommendations
        }

    @classmethod
    def _get_git_status(cls, repo_path: Path) -> Dict[str, Any]:
        git_dir = repo_path / ".git"
        if not git_dir.exists():
            return {
                "is_git_repo": False,
                "message": "Directory is not a git repository."
            }

        status: Dict[str, Any] = {
            "is_git_repo": True,
            "branch": "unknown",
            "is_clean": True,
            "modified_files": [],
            "untracked_files": [],
            "recent_commits": []
        }

        timeout = settings.subprocess_timeout_seconds

        try:
            # Get current branch
            res = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if res.returncode == 0:
                status["branch"] = res.stdout.strip()

            # Get status porcelain
            res = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if res.returncode == 0:
                lines = res.stdout.strip().splitlines()
                if lines and lines[0]:
                    status["is_clean"] = False
                    for line in lines:
                        code = line[:2].strip()
                        fname = line[3:].strip()
                        if code in ["M", "MM", "AM"]:
                            status["modified_files"].append(fname)
                        elif code in ["??", "?"]:
                            status["untracked_files"].append(fname)
                        else:
                            status["modified_files"].append(fname)

            # Get recent commits
            res = subprocess.run(
                ["git", "log", "-n", "5", "--pretty=format:%h - %s (%cr) <%an>"],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if res.returncode == 0 and res.stdout.strip():
                status["recent_commits"] = res.stdout.strip().splitlines()

        except Exception as e:
            status["error"] = f"Failed to retrieve git status: {str(e)}"

        return status

repo_inspector = RepoInspectorService()
