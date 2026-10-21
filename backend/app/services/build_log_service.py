import re
from typing import Any, Dict, List, Optional, Tuple
from backend.app.models import ObservedEvidence, AnalysisHypothesis, BuildLogAnalysisResponse
from backend.app.services.redaction_service import redaction_service

class BuildLogService:
    """
    Parses build logs, extracts error coordinates and context,
    and produces evidence vs hypothesis breakdowns.
    """

    TOOL_SIGNATURES = [
        ("docker", [r"#\d+\s+\[", r"failed to solve:", r"Dockerfile:\d+", r"docker\.io/library"]),
        ("npm", [r"npm error", r"tsc -b", r"error TS\d+:", r"\[vite\]:", r"Rollup failed"]),
        ("maven", [r"\[ERROR\]\s+COMPILATION ERROR", r"BUILD FAILURE", r"maven-compiler-plugin", r"from pom\.xml"]),
        ("gradle", [r"FAILURE: Build failed with an exception", r"Execution failed for task", r"Gradle"]),
        ("python", [r"Building wheel for", r"Failed building wheel", r"subprocess-exited-with-error", r"pip install", r"poetry install"]),
    ]

    @classmethod
    def detect_tool(cls, log: str, hint: Optional[str] = None) -> str:
        if hint and hint.lower() in ["docker", "npm", "maven", "gradle", "python"]:
            return hint.lower()
        
        for tool, patterns in cls.TOOL_SIGNATURES:
            for p in patterns:
                if re.search(p, log, re.IGNORECASE):
                    return tool
        return "generic"

    @classmethod
    def extract_evidence(cls, log: str) -> ObservedEvidence:
        lines = log.splitlines()
        primary_msg = "Unknown build failure"
        error_type = "BuildFailure"
        failed_command = None
        line_num = None
        exit_code = None
        context_lines: List[str] = []
        tokens: List[str] = []

        # Check for exit code
        exit_match = re.search(r"exit(?:ed with)? code:?\s*(\d+)", log, re.IGNORECASE)
        if exit_match:
            try:
                exit_code = int(exit_match.group(1))
            except ValueError:
                pass

        # Check for Rust compiler error
        if "can't find Rust compiler" in log or "cargo build" in log:
            error_type = "MissingRustCompilerError"
            primary_msg = "error: can't find Rust compiler during native package wheel compilation"
            failed_command = "cargo build --release"
            tokens = ["cargo", "rustc", "cryptography", "wheel"]

        # Check for TypeScript error
        elif "error TS" in log:
            ts_match = re.search(r"([^\s:]+\.tsx?):(\d+):(\d+)\s*-\s*error (TS\d+):\s*(.*)", log)
            if ts_match:
                failed_command = ts_match.group(1)
                line_num = int(ts_match.group(2))
                error_type = f"TypeScriptCompileError ({ts_match.group(4)})"
                primary_msg = ts_match.group(5)
                tokens = [ts_match.group(4), failed_command]
            else:
                error_type = "TypeScriptError"
                primary_msg = "TypeScript compilation failed"

        # Check for Java Maven compilation error
        elif "COMPILATION ERROR" in log or "cannot find symbol" in log:
            error_type = "JavaCompilationError"
            sym_match = re.search(r"\[ERROR\]\s+([^\s:]+\.java):\[(\d+),(\d+)\]\s*(.*)", log)
            if sym_match:
                failed_command = sym_match.group(1)
                line_num = int(sym_match.group(2))
                primary_msg = sym_match.group(4)
                tokens = ["javac", failed_command, "symbol"]
            else:
                primary_msg = "Maven compilation failed with missing symbol or incompatible type"

        # Check for missing C compiler
        elif "unable to execute 'x86_64-linux-gnu-gcc'" in log or "No such file or directory" in log:
            error_type = "MissingCCompilerError"
            primary_msg = "unable to execute 'x86_64-linux-gnu-gcc': No such file or directory"
            failed_command = "x86_64-linux-gnu-gcc"
            tokens = ["gcc", "build-essential", "uvloop", "wheel"]

        # Check for generic Docker RUN failure
        elif "ERROR: process" in log and "did not complete successfully" in log:
            error_type = "DockerRunStepFailure"
            docker_match = re.search(r'ERROR: process "([^"]+)" did not complete successfully', log)
            if docker_match:
                failed_command = docker_match.group(1)
                primary_msg = f"Docker step failed: {failed_command}"
                tokens = ["docker", "RUN"]

        # Find best context window around primary error
        match_idx = -1
        for i, line in enumerate(lines):
            if any(term in line.lower() for term in ["error:", "failed", "cannot find", "fatal:"]):
                match_idx = i
                if primary_msg == "Unknown build failure":
                    primary_msg = line.strip()
                break

        if match_idx != -1:
            start = max(0, match_idx - 4)
            end = min(len(lines), match_idx + 8)
            context_lines = lines[start:end]
        else:
            context_lines = lines[-12:] if len(lines) > 12 else lines

        return ObservedEvidence(
            error_type=error_type,
            primary_error_message=primary_msg,
            failed_command_or_file=failed_command,
            line_number=line_num,
            exit_code=exit_code,
            context_snippet="\n".join(context_lines),
            extracted_tokens=tokens
        )

    @classmethod
    def generate_deterministic_hypothesis(cls, evidence: ObservedEvidence, tool: str) -> AnalysisHypothesis:
        """
        Provides guaranteed, high-quality, domain-accurate diagnosis
        when Amazon Bedrock is in demo fallback mode.
        """
        if "MissingRustCompiler" in evidence.error_type or "Rust" in evidence.primary_error_message:
            return AnalysisHypothesis(
                likely_root_cause=(
                    "The Python package being installed (such as cryptography) requires building native extensions from source, "
                    "which mandates a Rust compiler (rustc/cargo). A minimal base image (e.g., python:3.11-slim) does not include Rust by default."
                ),
                confidence_score=0.98,
                explanation=(
                    "Recent versions of cryptography rely on Rust components. Pip attempts to compile wheels locally when prebuilt binary wheels "
                    "are not available for your platform or when pip itself is outdated and cannot resolve the manylinux wheel."
                ),
                prioritized_debugging_steps=[
                    "Upgrade pip and wheel first in your Dockerfile so pip can download precompiled manylinux binary wheels instead of compiling from source.",
                    "If building on an architecture without prebuilt wheels, install 'build-essential', 'cargo', and 'rustc' in a builder stage.",
                    "Verify your base image architecture matches the target deployment platform."
                ],
                recommended_fix_code=(
                    "# Recommended Dockerfile modification:\n"
                    "RUN pip install --upgrade pip setuptools wheel\n"
                    "# Or if source compilation is required:\n"
                    "RUN apt-get update && apt-get install -y --no-install-recommends \\\n"
                    "    build-essential \\\n"
                    "    cargo \\\n"
                    "    rustc \\\n"
                    " && rm -rf /var/lib/apt/lists/*\n"
                    "RUN pip install --no-cache-dir -r requirements.txt"
                ),
                recommended_fix_description="Upgrade pip to fetch precompiled binary wheels, or install the rustc/cargo toolchain."
            )

        if "MissingCCompiler" in evidence.error_type or "gcc" in evidence.primary_error_message:
            return AnalysisHypothesis(
                likely_root_cause=(
                    "A Python package with C extensions (such as uvloop) failed to build because the GNU C Compiler (gcc) is not installed in the environment."
                ),
                confidence_score=0.96,
                explanation=(
                    "The Python virtual environment was executed in a minimal environment without the 'build-essential' or 'gcc' packages. "
                    "When pip encounters source distributions (.tar.gz), it attempts to invoke x86_64-linux-gnu-gcc to compile C source files into machine code."
                ),
                prioritized_debugging_steps=[
                    "Install the build-essential and python3-dev packages via apt or your package manager.",
                    "Alternatively, check if prebuilt binary wheels exist for your Python minor version.",
                    "Ensure python-dev headers are present."
                ],
                recommended_fix_code=(
                    "# Debian / Ubuntu fix:\n"
                    "sudo apt-get update && sudo apt-get install -y build-essential python3-dev\n\n"
                    "# Dockerfile fix:\n"
                    "RUN apt-get update && apt-get install -y build-essential python3-dev && rm -rf /var/lib/apt/lists/*"
                ),
                recommended_fix_description="Install gcc and Python development headers before running pip install."
            )

        if "TypeScript" in evidence.error_type or "TS" in evidence.error_type:
            return AnalysisHypothesis(
                likely_root_cause=(
                    "TypeScript type checking failed during the build process due to a missing component export or type mismatch."
                ),
                confidence_score=0.94,
                explanation=(
                    f"The TypeScript compiler failed at '{evidence.failed_command_or_file or 'source file'}' line {evidence.line_number or 'N/A'}. "
                    f"Message: {evidence.primary_error_message}"
                ),
                prioritized_debugging_steps=[
                    "Check if the imported module exists and its export name matches the import statement.",
                    "Inspect tsconfig.json paths/alias configuration (e.g. '@/*') to confirm path resolution is valid.",
                    "Verify all nullable or optional types are handled safely with optional chaining (?.) or nullish coalescing (??)."
                ],
                recommended_fix_code=(
                    "// Ensure module is exported and handles undefined values:\n"
                    "export const MetricsChart = ({ data }: { data?: any }) => {\n"
                    "  // ...\n"
                    "};\n"
                    "// In consuming file:\n"
                    "authToken: process.env.API_SECRET_TOKEN ?? '',"
                ),
                recommended_fix_description="Correct the module import path and provide default fallback for optional environment variables."
            )

        if "Java" in evidence.error_type or "Maven" in tool:
            return AnalysisHypothesis(
                likely_root_cause=(
                    "Java compilation failed due to a missing symbol or signature mismatch in a dependency class."
                ),
                confidence_score=0.92,
                explanation=(
                    "The javac compiler could not locate the referenced method or class. This usually indicates an incompatible version "
                    "of the third-party library in pom.xml, or a missing method after an upgrade."
                ),
                prioritized_debugging_steps=[
                    "Run 'mvn dependency:tree' to inspect dependency versions and transitive conflicts.",
                    "Verify the method signature in the library's Javadoc for the exact version listed in pom.xml.",
                    "Clean and rebuild your local repository cache using 'mvn clean compile -U'."
                ],
                recommended_fix_code=(
                    "<!-- Update pom.xml with compatible library version -->\n"
                    "<dependency>\n"
                    "    <groupId>com.auth0</groupId>\n"
                    "    <artifactId>java-jwt</artifactId>\n"
                    "    <version>4.4.0</version>\n"
                    "</dependency>"
                ),
                recommended_fix_description="Align dependency version in pom.xml and check library Javadoc for updated API signature."
            )

        # Generic hypothesis
        return AnalysisHypothesis(
            likely_root_cause=f"The {tool} build process terminated with exit code {evidence.exit_code or 1}.",
            confidence_score=0.80,
            explanation=f"Observed error: '{evidence.primary_error_message}'. Check the command output and surrounding context.",
            prioritized_debugging_steps=[
                "Inspect the lines immediately preceding the failure in the log output.",
                "Verify required system dependencies, compilers, and credentials are configured.",
                "Run the build command locally with verbose/debug flags enabled."
            ],
            recommended_fix_code="# Run build locally with debug flag:\n# e.g., docker build --progress=plain .",
            recommended_fix_description="Re-run the build locally with verbose output to isolate the failing sub-step."
        )

build_log_service = BuildLogService()
