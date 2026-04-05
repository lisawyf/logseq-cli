# Command Mapping

Use these commands as the first choice for common requests.

## Graph Setup

- Check graph resolution:

```bash
logseq-cli graph detect --json
```

- Set the default graph:

```bash
logseq-cli graph use --graph /path/to/Logseq
```

## Project Context

- Project summary:

```bash
logseq-cli summarize project "Project Alpha" --json
```

- Project backlinks:

```bash
logseq-cli links backlinks "Project Alpha" --json
```

- Read the main project page:

```bash
logseq-cli page read "Project Alpha" --json
```

## Topic Context

- Topic summary:

```bash
logseq-cli summarize topic "ops" --json
```

- Tag search:

```bash
logseq-cli search tags "ops" --json
```

- Text search:

```bash
logseq-cli search text "ops" --json
```

## Daily And Weekly Recall

- Daily summary:

```bash
logseq-cli summarize daily --today --json
```

- Daily summary for a specific date:

```bash
logseq-cli summarize daily --date 2026-04-05 --json
```

- Weekly summary:

```bash
logseq-cli summarize weekly --date 2026-04-05 --json
```

- Read a journal:

```bash
logseq-cli journal read --date 2026-04-05 --json
```

## Open Work

- Open tasks:

```bash
logseq-cli tasks list --state todo,doing,now,waiting,later --json
```

## Decisions And Rationale

- Decision records for a topic:

```bash
logseq-cli decisions list "MBB" --json
```

- Decision records in a date window:

```bash
logseq-cli decisions list "OpenClaw" --since 2026-01-01 --until 2026-04-01 --json
```

- Decision card for a topic:

```bash
logseq-cli cards build decision "MBB" --json
```

## Lessons And Best Practices

- Lessons for a topic:

```bash
logseq-cli lessons list "MBB" --json
```

- Lessons in a date window:

```bash
logseq-cli lessons list "ops" --since 2026-01-01 --until 2026-04-01 --json
```

- Lesson card for a topic:

```bash
logseq-cli cards build lesson "MBB" --json
```

## Safe Write-Back

- Quick note into today's journal:

```bash
logseq-cli capture quick --today --text "Captured note" --json
```

- Capture a follow-up task:

```bash
logseq-cli capture task --today --text "Follow up with team" --json
```

- Capture a project update:

```bash
logseq-cli capture project "Project Alpha" --text "Investigated issue" --json
```

## Retrieval Heuristics

- Start with `summarize` when the user wants overview or recall.
- Start with `tasks list` when the user asks what is pending.
- Start with `search` when the user gives a keyword, tag, or loosely named topic.
- Use `page read` or `journal read` only when the aggregate result is not enough.
- Keep context tight. Usually 3 to 10 matched items is enough.
