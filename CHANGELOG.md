# Changelog

## 0.2.0 - 2026-04-05

Second local CLI release with a substantially expanded retrieval surface for
Claude Code and other local coding agents.

Added command groups and higher-level knowledge workflows:

- `graph`: `use`
- `decisions`: `list`
- `lessons`: `list`
- `cards build`: `topic`, `tag`, `project`, `decision`, `lesson`, `weekly`
- `recall`: `topic`
- `timeline`: `topic`

Expanded behavior since `0.1.0`:

- Claude Code integration now includes a dedicated skill package with `SKILL.md`,
  command references, and install helpers.
- topic recall now builds answer-ready evidence packs from scattered page and
  journal matches.
- topic timelines now aggregate journal history into chronological views.
- decision extraction now pulls likely decisions plus inline or child-block
  rationale snippets.
- lesson extraction now pulls best practices, pitfalls, notes-to-self, and
  reusable takeaways.
- cards now compress topics, tags, projects, decisions, lessons, and weekly
  journal windows into compact summary objects suitable for model consumption.
- configurable aliases and synonyms in `config.toml` now expand shorthand terms
  such as `MBB` across search, recall, cards, decisions, lessons, and topic
  summaries.
- release automation now includes a repository-local `scripts/release.sh`
  helper for checks, smoke tests, and local artifact builds.

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
