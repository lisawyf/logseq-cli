---
description: Check whether my local Logseq knowledge base is ready for Claude
argument-hint: none
---

Check whether `logseq-cli` can resolve my default graph and summarize the current graph status.

Run:
- `logseq-cli graph detect --json`
- `logseq-cli graph stats --json`

Then:
1. Report whether the default graph is configured and reachable.
2. Report the graph root if found.
3. Summarize the graph size briefly.
4. If graph detection fails, tell me exactly to run `logseq-cli graph use --graph /path/to/Logseq`.

