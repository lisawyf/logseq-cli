---
description: Turn journals and tasks into a short next-actions plan
argument-hint: [date optional: YYYY-MM-DD]
---

Build a next-actions plan from my local Logseq graph.

If no date is provided, run:
- `logseq-cli summarize daily --today --json`
- `logseq-cli tasks list --state todo,doing,now,waiting,later --json`

If a date is provided, run:
- `logseq-cli summarize daily --date "$ARGUMENTS" --json`
- `logseq-cli tasks list --state todo,doing,now,waiting,later --json`

Then produce:
1. The highest-signal unfinished work.
2. What I likely intended to do next.
3. A concrete next-actions list with at most 5 items.
4. Any missing context I should retrieve with a follow-up Logseq query.

