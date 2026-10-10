# Validation recorded October 10, 2026

Python 3.11 on Windows. Nine tests passed. Ruff passed, JavaScript syntax validation passed, and `pip check` found no broken requirements. `pip-audit` reported no known vulnerabilities for the pinned runtime requirements at the time of this check; that is a time-specific package advisory check, not a comprehensive security certification.

The first added network-access test incorrectly restarted the same MCP session manager twice. It was corrected to construct a fresh application for each server lifecycle; the final full suite passed. One upstream Starlette/httpx deprecation warning remains.

Automated evidence: `evidence/pytest.txt`, `evidence/ruff.txt`, `evidence/dependencies.txt`, `audit.json`.

The real Streamable HTTP MCP test launches a separate Uvicorn process with a temporary SQLite database, initializes protocol `2025-11-25`, exercises six tools, and terminates the server afterwards. Store and REST tests cover acceptance, rejection, persistence, stale versions, concurrent writes, retry deduplication, timezones, bearer-token access and origin/loopback restrictions.

Browser evidence: fictional members Alex and Mira created a task, proposed a handoff, accepted it, reloaded, then completed it. Three screenshots capture these actual states. A 390px mobile layout was inspected: document scroll width was 390px and all input/select controls had associated labels. This is a basic responsive/accessibility check, not a comprehensive accessibility audit. Speech synthesis was not audibly evaluated.

The app ran at http://127.0.0.1:8741/. This is a local preview. Docker instructions and hosted deployment remain unverified. No real Alexa host connection or operational household field study was performed. Evidence supports integrated laboratory prototype maturity (TRL 4).
