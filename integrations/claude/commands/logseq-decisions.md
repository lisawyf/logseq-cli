---
description: Pull decision history and rationale from my local Logseq graph
argument-hint: [topic, project, or decision area]
---

Investigate decision history for "$ARGUMENTS" using my local Logseq graph.

Run:
- `logseq-cli cards build decision "$ARGUMENTS" --json`
- `logseq-cli decisions list "$ARGUMENTS" --json`

Then produce:
1. The main decisions I already made.
2. The strongest reasons or tradeoffs recorded in my notes.
3. What appears settled vs what still seems open.
4. A short recommendation section based on the retrieved evidence.

Clearly distinguish retrieved facts from your synthesis.

