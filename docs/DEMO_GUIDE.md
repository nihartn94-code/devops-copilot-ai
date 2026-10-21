# DevOps Copilot AI — 3-Minute Hackathon Demo Script

This script walks through the core capabilities of **DevOps Copilot AI** during a hackathon evaluation or live demonstration.

---

## ⏱️ Video / Live Walkthrough Timeline (Total: 2 min 45 sec)

### [0:00 - 0:30] Introduction & Problem Statement
- **Narrator**: *"Every day, developers lose hours deciphering cryptic Docker build failures, broken npm packages, and failed CI test suites. DevOps Copilot AI is our intelligent developer assistant built on Amazon Bedrock and the Model Context Protocol."*
- **Action**: Show Dashboard with aggregate statistics, recent analysis feed, and system health status. Note that Demo Mode fallback is clearly flagged if running without live AWS credentials.

### [0:30 - 1:15] Build-Log Analysis with Secret Redaction
- **Narrator**: *"Let's upload a failing Docker build log. Notice in the log that there's an accidentally leaked AWS secret key."*
- **Action**: Select the sample Docker build log (`sample-data/logs/docker-build-fail.log`).
- **Narrator**: *"DevOps Copilot automatically redacts the secret before processing. It separates the **Observed Evidence** (Rust compiler missing during cryptography wheel build) from the **AI Hypothesis** and provides a drop-in Dockerfile fix."*
- **Action**: Show the parsed error breakdown, root cause explanation, and the "Copy Recommended Fix" action.

### [1:15 - 1:45] Repository & Git Inspection
- **Narrator**: *"Next, let's inspect an authorized repository directory. DevOps Copilot never scans unauthorized paths."*
- **Action**: Click "Inspect Repo", choose `sample-data/sample-repo`.
- **Narrator**: *"It detects the tech stack (Node.js/Express/Jest), identifies uncommitted git changes, and checks configuration files for best practices."*
- **Action**: Point out Git status, detected dependencies, and identified security recommendations.

### [1:45 - 2:15] Test Analyzer & Documentation Search
- **Narrator**: *"Let's paste a failing pytest run. The analyzer immediately identifies the failed assertions, isolates the 500 error vs expected 422, and explains the Pydantic ValidationError."*
- **Action**: Run Test Analyzer with `sample-data/tests/pytest-failure.txt`.
- **Action**: Switch to Doc Assistant, type *"How to fix missing Rust compiler in Docker?"*. Show the grounded search results with verified documentation links.

### [2:15 - 2:45] Model Context Protocol (MCP) & Alexa+ Integration
- **Narrator**: *"DevOps Copilot AI isn't just a web app—it runs a self-hosted MCP server over Streamable HTTP. Any MCP client or Alexa+ device can invoke tools like `analyze_build_log` or `inspect_repository` in real-time."*
- **Action**: Show the MCP server running on port 8001 and execute an MCP tool call showing structured JSON responses.
- **Narrator**: *"DevOps Copilot AI: Faster debugging, safer codebases, and seamless AI agent interoperability."*
