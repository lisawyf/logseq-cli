---
description: Build a daily brief from my Logseq journal and open tasks
argument-hint: [date optional: YYYY-MM-DD]
---

If no date is provided, use today.

If no arguments are provided, run:
- `logseq-cli summarize daily --today --json`
- `logseq-cli tasks list --state todo,doing,now,later,waiting --json`

If a date is provided, run:
- `logseq-cli summarize daily --date "$ARGUMENTS" --json`
- `logseq-cli tasks list --state todo,doing,now,later,waiting --json`

Then produce:
1. What I worked on.
2. What is still in progress.
3. The top 3 priorities I should focus on next.
4. A short standup-style update I can reuse.

