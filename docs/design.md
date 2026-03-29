# design.md

## 1. Project overview

This project implements a local command-line tool named `logseq-cli` for working with **file-based Logseq graphs**.

The tool is intended for:
- local shell usage
- Codex
- Claude Code
- OpenClaw
- other local agents and scripts

The tool operates directly on local files and does **not** depend on Logseq Desktop being open.

This project is intentionally **CLI-only**.

---

## 2. Explicit non-goals

The following are explicitly out of scope:

- MCP support
- HTTP server mode
- daemon mode
- web UI
- network APIs of any kind
- Logseq DB graph support
- Logseq plugin runtime integration
- OCR
- PDF parsing
- semantic search
- full-fidelity document editing
- rich editor behavior

Do not implement any network-facing interface.
Do not add service mode.
Do not add remote APIs.

---

## 3. Product goal

The goal is to provide a safe, scriptable, local CLI that can:

- discover a Logseq file graph
- read pages and journals
- search text
- extract tasks
- inspect links
- append notes conservatively
- produce stable machine-readable JSON for agent consumption

This tool is not meant to replace Logseq itself.
It is meant to provide a reliable local automation layer over Logseq’s file-based notes.

---

## 4. Supported graph type

Supported graph type:
- file-based Logseq graph

Typical structure:

```text
GRAPH_ROOT/
├── journals/
├── pages/
├── assets/
└── logseq/

A graph root is usually identified by:

the presence of journals/ and pages/, or
the presence of logseq/config.edn
5. Supported formats

Primary format:

Markdown (.md)

Secondary format:

Org-mode (.org) with limited early support

Early development should focus on Markdown correctness first.
Org support can remain partial in early milestones.

6. Design principles

When making design decisions, prioritize in this order:

correctness
safe write behavior
stable JSON output
maintainability
breadth of features

Additional design rules:

keep the CLI surface predictable
keep output stable for automation
keep writes conservative
keep parsing logic reusable
keep implementation easy for future agents to extend
prefer explicit behavior over clever behavior
avoid large unrelated refactors
7. CLI model

Command shape:

logseq-cli <resource> <action> [options]

Primary resources:

graph
page
journal
search
tasks
links
capture
summarize

The CLI must be usable both by humans and by local agents/scripts.

8. MVP scope

The MVP must implement:

graph detect
page read
page list
journal read
journal append
search text
tasks list

All MVP commands must support:

--json

Helpful additional output modes:

--raw
--quiet

The MVP should be fully working before expanding into additional commands.

9. Planned command groups
9.1 graph
graph detect
graph stats
9.2 page
page read
page list
page create
page append
page append-under
9.3 journal
journal read
journal list
journal ensure
journal append
journal summarize
9.4 search
search text
search links
search tags
9.5 tasks
tasks list
tasks summary
9.6 links
links backlinks
links outgoing
9.7 capture
capture quick
capture project
capture task
9.8 summarize
summarize daily
summarize weekly
summarize project
summarize topic

Only the MVP commands are required first.

10. Output requirements

The CLI must support:

human-readable output
machine-readable JSON output via --json

Preferred JSON envelope:

{
  "ok": true,
  "command": "page read",
  "graph_root": "/path/to/graph",
  "data": {},
  "warnings": [],
  "errors": []
}

Failure example:

{
  "ok": false,
  "command": "page read",
  "graph_root": "/path/to/graph",
  "data": null,
  "warnings": [],
  "errors": [
    {
      "code": "PAGE_NOT_FOUND",
      "message": "Page 'OpenClaw' not found"
    }
  ]
}

Rules:

stdout for normal results
stderr for diagnostics and errors
avoid extra prose in JSON mode
keep field names stable over time
11. Exit codes

Use stable exit codes:

0 success
1 general failure
2 invalid arguments
3 graph not found
4 page not found
5 write conflict
6 parse failure
12. Graph discovery behavior

Graph resolution order:

explicit --graph
configured default graph
current directory upward auto-discovery

The tool should work predictably even when no graph is explicitly passed.

13. Page resolution behavior

Page names and file names may not map exactly.

When resolving a page name, try in this order:

exact filename match
case-insensitive filename match
normalized match across spaces, underscores, and hyphens
first heading title match
page property title match

Support Chinese page names and filenames.

14. Parsing model

The internal model should represent:

graph
document
block
search hit
task item / task summary
Markdown parsing priorities

Support these Logseq-like Markdown structures first:

bullet/list blocks
indentation-based nesting
TODO states
page refs [[Page]]
tags #tag
headings
block refs ((uuid))
SCHEDULED:
DEADLINE:
common page/block properties

Example:

- TODO Fix gateway token issue #openclaw
  SCHEDULED: <2026-03-30 Mon>
  DEADLINE: <2026-03-31 Tue>
  - Confirmed env var was not injected

The parser should extract:

todo state
content
tags
page refs
scheduled
deadline
nested child blocks
Org support

Early Org support may be limited to:

headings
TODO
tags
scheduled
deadline
basic text

Full write support for Org is not required in early versions.

15. Write model

Writes must be conservative.

Allowed early writes:

create a page
append to page end
append under heading
append to journal
ensure journal exists

Avoid:

broad rewrites
arbitrary reordering
full document reformatting
hidden destructive changes

Write options should support:

--dry-run
--backup
--backup-dir
--no-backup

Recommended write flow:

read original file
parse and validate
generate updated content
optionally show or compute diff
write atomically with temp file replacement
16. Indexing strategy

The first implementation should prefer direct file scanning.

Do not require a database or service.
Do not optimize prematurely.

A lightweight cache/index may be added later if needed, but the MVP should work without it.

17. Summarization strategy

The CLI itself should not embed an LLM.

summarize commands should initially be rule-based and produce structured output that local agents can reuse.

Examples of structured summary material:

recent documents touched
frequent page refs
frequent tags
task counts
candidate highlights
raw snippets

This keeps the CLI deterministic and scriptable.

18. Configuration

Optional config file path:

~/.config/logseq-cli/config.toml

Typical config values:

default graph path
default output mode
backup behavior
search defaults
org read/write settings

Command-line arguments must override config values.

19. Suggested repository structure
src/logseq_cli/
  __init__.py
  main.py
  cli/
  core/
  utils/
tests/
  fixtures/
docs/

Guidelines:

keep CLI argument handling in cli/
keep parsing/search/task/write logic in core/
keep shared helpers in utils/
20. Testing expectations

The repository must include tests for:

graph detection
page resolution
markdown block parsing
task extraction
page ref extraction
text search
append behavior

Fixtures should include:

multiple pages
multiple journals
nested blocks
TODO states
tags
scheduled/deadline dates
page refs
Chinese page names
ambiguous page-name cases
21. Definition of done for MVP

The MVP is complete when all of the following are true:

graph detect works
page read works
page list works
journal read works
journal append works safely
search text works
tasks list works
all MVP commands support --json
tests cover core paths
README documents installation and usage correctly