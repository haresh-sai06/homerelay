# HomeRelay — local submission draft

Status: project and written materials prepared. No Devpost submission or registration receipt exists.

**Tagline:** Ask for help. Keep responsibility clear.

## Inspiration

An errand can fall through the gap between “can you take this?” and an actual agreement. We wanted a household board that treats a handoff as a request requiring acceptance.

## What it does

HomeRelay records household tasks with owners and due dates. An owner proposes a handoff; the recipient accepts or declines. The original owner remains responsible until acceptance. Members see their own open tasks, overdue tasks and pending handoffs, and can read a factual briefing aloud using browser speech synthesis.

## How it was built

The browser uses HTML, CSS and vanilla JavaScript. FastAPI exposes validated REST endpoints. A SQLite store handles durable state, ordered event history, optimistic task versions and idempotent task creation. The MCP Python SDK exposes six Streamable HTTP tools so a compatible AI host can read the board and perform confirmed changes. An integration test uses a real MCP client and a separately launched HTTP server.

## Challenges and lessons

The important failure case was a proposed handoff being mistaken for acceptance. Keeping those transitions separate and rejecting stale versions makes responsibility explicit. MCP structured responses also required concrete dictionary return annotations for consistent client consumption. The workflow was checked at the store, REST, MCP and browser levels.

## Accomplishments

A complete local create → propose → accept → reload → complete journey, nine passing automated tests, a functional interface, and three actual application screenshots. These are engineering demonstrations, not evidence of adoption or market impact.

## Next steps

Evaluate with real households, add individual authentication and household isolation, improve accessibility with user testing, and verify an authorized deployment. No customer study has been conducted.

## Disclosure

New application source was developed on October 10, 2026 with extensive Codex AI assistance. Public dependencies were used; no existing project source was reused. No Alexa connection, external LLM session or sponsor-specific integration is claimed. Proposed team: Haresh Sainaath and Shyam Prasath S; account linking and actual contribution descriptions remain pending. Do not invent teammate work.

Repository: https://github.com/haresh-sai06/homerelay (verify after publication).
Public live demo: pending, not deployed. Local demo: http://127.0.0.1:8741/.
Video: `docs/evidence/homerelay-demo.mp4`, a 2:42 English-captioned capture of the actual browser workflow. The recording uses timestamped browser frames and preserves elapsed time between captures; it has no audio. A portal-supported public video URL remains to be verified. Screenshots: `docs/evidence/01-pending-handoff.jpg`, `02-accepted-handoff.jpg`, `03-completed.jpg`.

## Next Byte Hacks V5 compliance

This is a proposed exclusive first target, not an existing submitted entry. The official rules require new work during the event, accessible source, screenshots and a demo video. A 2–3 minute video fits both the overview's 1–3 minute and rules' 2–5 minute limits. Both participants must personally review the eligibility and legal terms. The AI clause prohibits policy-violating AI code; it does not expressly endorse unrestricted autonomous development, so retain that nuance and confirm the intended assistance level before final submission. Cross-submission permission is unknown; do not submit this project to a second event without verifying both policies.
