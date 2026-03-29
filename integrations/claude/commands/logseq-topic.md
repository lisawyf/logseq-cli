---
description: Summarize a recurring topic, tag, or theme from local Logseq
argument-hint: [topic or tag]
---

Investigate the topic "$ARGUMENTS" across my local Logseq graph.

Run:
- `logseq-cli summarize topic "$ARGUMENTS" --json`
- `logseq-cli search tags "$ARGUMENTS" --json`
- `logseq-cli search text "$ARGUMENTS" --json`

Then produce:
1. Recurring patterns or themes.
2. Frequently associated projects, pages, or journals.
3. Open questions, tasks, or unresolved issues.
4. Concrete ways I could standardize, document, or improve this area.

