# Docker Build Debugging & Common Failure Resolution

Source: https://docs.docker.com/build/troubleshooting/

## Common Docker Build Failures

### 1. `can't find Rust compiler` / C Extension Compilation
**Cause**: Installing Python packages that compile native extensions (e.g., `cryptography`, `pydantic-core`, `uvloop`, `tiktoken`) on slim Debian/Alpine images where prebuilt wheels are not available or pip is outdated.
**Fix**:
- Upgrade pip, setuptools, and wheel first: `RUN pip install --upgrade pip setuptools wheel`
- Or install build dependencies in a builder stage:
  ```dockerfile
  RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      gcc \
      cargo \
      rustc \
      libpq-dev \
      && rm -rf /var/lib/apt/lists/*
  ```

### 2. Failed to Solve with Exit Code 1
**Cause**: A `RUN` command failed, or a file referenced in `COPY` does not exist in the build context.
**Fix**:
- Check `.dockerignore` to ensure the required files aren't ignored.
- Use `DOCKER_BUILDKIT=1 docker build --progress=plain .` to view full unbuffered output.

### 3. Out of Memory (OOM) Killed (Exit Code 137)
**Cause**: Memory-intensive compilation (like Node/Webpack or C++ builds) exceeded container limits.
**Fix**: Increase Docker daemon memory limit or configure `NODE_OPTIONS=--max-old-space-size=4096`.
