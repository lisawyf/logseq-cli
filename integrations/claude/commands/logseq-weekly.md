---
description: Build a weekly brief from my local Logseq journals
argument-hint: [date optional: YYYY-MM-DD]
---

If no date is provided, use today as the weekly anchor.

If no arguments are provided, run:
- `logseq-cli cards build weekly --today --json`

If a date is provided, run:
- `logseq-cli cards build weekly --date "$ARGUMENTS" --json`

Then produce:
1. The key work themes from the week.
2. The most important open tasks.
3. The projects and topics that appeared most often.
4. A concise weekly brief I can reuse in planning or reporting.

Clearly label facts vs inference.

