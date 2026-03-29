---
description: Pull targeted context from my local Logseq knowledge base
argument-hint: [topic or project]
---

Use my local Logseq knowledge base to gather only the most relevant context about "$ARGUMENTS".

Start with:
- `logseq-cli search text "$ARGUMENTS" --json`
- `logseq-cli search links "$ARGUMENTS" --json`
- `logseq-cli search tags "$ARGUMENTS" --json`
- `logseq-cli summarize topic "$ARGUMENTS" --json`

If the query appears to be a project or page name, also run:
- `logseq-cli summarize project "$ARGUMENTS" --json`

If retrieval is still ambiguous, read at most one highly relevant page or journal.

Then produce:
1. The most relevant facts from my Logseq history.
2. Relevant pages or journals.
3. Open tasks or follow-ups if present.
4. A short "what matters now" section.

Clearly label facts vs inference.

