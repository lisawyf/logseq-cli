---
description: Capture a result or note back into my Logseq graph
argument-hint: [free-form note or project + result]
---

I want to write something back into my Logseq graph.

Interpret "$ARGUMENTS" conservatively.

Rules:
- If it is clearly just a note for today, prefer `logseq-cli capture quick --today --text "<note>" --json`.
- If it is clearly tied to a project, prefer `logseq-cli capture project "<project>" --text "<note>" --json`.
- If it is clearly a next action or follow-up task, prefer `logseq-cli capture task --today --text "<task>" --json`.
- If both a project and a task are present, include the project on the task capture.

Before writing, summarize in one sentence what you are about to capture and where.
If the intended write target is ambiguous, ask a clarifying question instead of guessing.

