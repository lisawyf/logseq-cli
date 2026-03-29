---
description: Summarize a project from local Logseq history
argument-hint: [project name]
---

Build a focused project brief for "$ARGUMENTS" using my local Logseq graph.

Run:
- `logseq-cli summarize project "$ARGUMENTS" --json`
- `logseq-cli links backlinks "$ARGUMENTS" --json`
- `logseq-cli tasks list --json`

If needed, read one highly relevant page:
- `logseq-cli page read "$ARGUMENTS" --json`

Then produce:
1. Current project status.
2. Known risks or blockers.
3. Related tasks that are still open.
4. Recommended next steps.

Clearly distinguish what was found in Logseq from your synthesis.

