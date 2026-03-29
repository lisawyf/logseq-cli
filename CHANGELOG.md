# Changelog

## 0.1.0 - 2026-03-29

Initial local CLI-only release for file-based Logseq graphs.

Implemented command groups:

- `graph`: `detect`, `stats`
- `page`: `list`, `read`, `create`, `append`, `append-under`
- `journal`: `list`, `read`, `ensure`, `append`, `summarize`
- `search`: `text`, `links`, `tags`
- `tasks`: `list`
- `links`: `backlinks`, `outgoing`
- `capture`: `quick`, `project`, `task`
- `summarize`: `daily`, `weekly`, `project`, `topic`

Release notes:

- local file access only, with no MCP, HTTP, daemon, or network interface
- stable JSON envelopes across implemented commands
- conservative append-oriented write behavior
- Markdown-first parsing with limited Org support
- `--quiet` support across implemented commands
- regression coverage for JSON contract, write flows, search behavior, capture flows, and summaries
