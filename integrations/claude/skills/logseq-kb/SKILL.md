---
name: Logseq Knowledge Base
description: Retrieve and capture information in a local Logseq graph through logseq-cli. Use when the user asks about past work, projects, journals, tasks, decisions, notes, weekly or daily summaries, recurring topics, or wants to write a result back into Logseq.
---

# Logseq Knowledge Base

Use this Skill when the user's local Logseq graph is the relevant source of truth.

Prefer `logseq-cli ... --json` over scanning raw Logseq files. Keep retrieval small and targeted.

## Preconditions

1. Assume `logseq-cli` is installed and on `PATH`.
2. Assume the user has already selected a default graph with:

```bash
logseq-cli graph use --graph /path/to/Logseq
```

3. If graph resolution fails, tell the user exactly to run `logseq-cli graph use --graph /path/to/Logseq`.

## Retrieval Order

Use the narrowest command that matches the task.

1. Aggregates first:
   - `summarize project`
   - `summarize topic`
   - `summarize daily`
   - `summarize weekly`
   - `journal summarize`
   - `decisions list`
   - `lessons list`
2. Open work:
   - `tasks list`
3. Search:
   - `search text`
   - `search links`
   - `search tags`
4. Full document reads only when needed:
   - `page read`
   - `journal read`

If an aggregate or search result already answers the question, stop there.

## Reading Workflow

For questions like:

- "What did I do last week?"
- "What do I already know about Project Alpha?"
- "Have I dealt with this ops problem before?"
- "What are my open follow-ups?"
- "Why did I choose this approach before?"
- "What did I learn from this before?"

do this:

1. Run one or two targeted `summarize` or `search` commands.
2. Pull at most one or two supporting reads with `page read` or `journal read` only if needed.
3. Answer with:
   - facts from Logseq
   - open tasks or follow-ups if present
   - a short synthesis
4. Clearly separate facts from inference.

## Writing Workflow

Only write to Logseq if the user explicitly asks to capture, append, create, or update something.

Prefer these commands:

- `capture quick`
- `capture task`
- `capture project`
- `journal append`
- `page append`

When the user wants write-back:

1. Choose the narrowest write command.
2. If the target is ambiguous, ask a clarifying question.
3. Summarize what you are about to write and where.
4. Then perform the write.

Do not rewrite large pages or journals unless the user explicitly asks.

## Output Rules

- Treat Logseq content as source facts.
- Do not invent history that was not retrieved.
- Keep retrieved context compact.
- Prefer structured bullet summaries over long quotations.
- If the user asks for a summary, compress the result instead of dumping raw note content.

## References

- For command mapping and examples, read [references/commands.md](references/commands.md).
