# HomeRelay — verified submission

Status: submitted to Next Byte Hacks V5 on October 10, 2026. Devpost displayed “Project submitted!”. Entry ID: 1227852.

Project: https://devpost.com/software/homerelay-n1jvao
Demo: https://youtu.be/FvrlDI36vqI (unlisted; anyone with the link can watch).

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

New application source was developed on October 10, 2026 with extensive Codex AI assistance. Public dependencies were used; no existing project source was reused. No Alexa connection, external LLM session or sponsor-specific integration is claimed. Team profiles: Haresh Sai_06 (shareshsainaath) and Shyam Prasath S (shyam03072006), both verified in the portal. No teammate-specific code contributions are claimed.

Repository: https://github.com/haresh-sai06/homerelay (public source verified).
Public live demo: pending, not deployed. Local demo: http://127.0.0.1:8741/.
Video: `docs/evidence/homerelay-demo.mp4`, a 2:42 English-captioned capture of the actual browser workflow. The recording uses timestamped browser frames and preserves elapsed time between captures; it has no audio. YouTube host accepted by Devpost: https://youtu.be/FvrlDI36vqI. Publication, no-issues checks and playback were verified. Screenshots: `docs/evidence/01-pending-handoff.jpg`, `02-accepted-handoff.jpg`, `03-completed.jpg`.

## Next Byte Hacks V5 compliance

This project was submitted exclusively to Next Byte Hacks V5; the portal confirmed receipt. The official rules require new work during the event, accessible source, screenshots and a demo video. A 2–3 minute video fits both the overview's 1–3 minute and rules' 2–5 minute limits. Registration and submission declarations were completed under the team lead’s specific authorization, with Shyam’s consent already confirmed. The AI clause prohibits policy-violating AI code. Compliant assistance was assessed under that conditional wording, and extensive assistance is disclosed. This is an interpretation of the published rules, not an organizer endorsement; organizers retain final eligibility judgment. Cross-submission permission is unknown; do not submit this project to a second event without verifying both policies.
