# AGENTS.md

This repository builds a local CLI tool named `logseq-cli` for **file-based Logseq graphs**.

Read and follow this file before making changes.

---

## 1. Project goal

Build and maintain a Python CLI that works directly on **file-based Logseq graphs** stored on local disk.

Primary users:
- Codex
- Claude Code
- OpenClaw
- local shell scripts and automation

This project is **CLI-only**.

The tool must:
- work on local files directly
- not depend on Logseq Desktop being open
- not implement MCP
- not implement HTTP server mode
- not implement daemon mode
- not implement any network API
- produce stable machine-readable output
- be safe for local note data
- be easy for future agents to extend

---

## 2. Scope

### In scope
- file-based Logseq graphs
- Markdown `.md` support as first priority
- Org-mode `.org` limited early support
- graph discovery
- page read/list/create
- journal read/list/append/ensure
- text search
- task extraction
- backlinks / outgoing links
- conservative append-style write operations
- rule-based summaries
- stable `--json` output

### Out of scope
- Logseq DB graph
- Logseq plugin runtime integration
- MCP
- HTTP server mode
- daemon/server architecture
- network APIs of any kind
- image OCR
- PDF parsing
- semantic search
- rich editor behavior
- broad document rewrites

Do not add any remote interface.
Do not add any background service.
Operate on local files only.

---

## 3. Core design principles

When making tradeoffs, prioritize in this order:

1. correctness
2. safe write behavior
3. stable JSON output
4. maintainability
5. feature breadth

Additional rules:
- keep the CLI layer thin
- keep parsing, searching, task extraction, and writing logic in core modules
- prefer explicit code over clever code
- avoid overengineering
- keep diffs scoped to the task
- do not introduce unrelated refactors
- do not add network-facing functionality

---

## 4. Expected graph structure

Typical file-based Logseq graph:

```text
GRAPH_ROOT/
├── journals/
├── pages/
├── assets/
└── logseq/

Graph discovery should check:

explicit --graph
config file default graph
current directory upward auto-discovery

A directory is likely a graph root when it contains:

journals/ and pages/, or
logseq/config.edn
5. Primary technology choices

Use:

Python 3.11+
Typer
Pydantic
Pytest
pathlib

Allowed supporting libraries:

rich
orjson
rapidfuzz
python-dateutil

Do not add heavy infrastructure or database dependencies unless clearly justified.

6. Required CLI shape

Command format:

logseq-cli <resource> <action> [options]

Main resources:

graph
page
journal
search
tasks
links
capture
summarize
7. MVP requirements

The first usable version must include:

graph detect
page read
page list
journal read
journal append
search text
tasks list

All MVP commands must support --json.

If time or context is limited, complete the MVP fully before moving to enhancements.

8. JSON output contract

Machine-readable JSON is a core requirement.

Preferred response shape:

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

stdout = results
stderr = diagnostics/errors
no extra commentary in JSON mode
keep field names stable

Support where relevant:

--json
--raw
--quiet
optionally --jsonl for search-like output
9. Stable exit codes

Use these exit codes consistently:

0 success
1 general failure
2 invalid arguments
3 graph not found
4 page not found
5 write conflict
6 parse failure
10. Write safety rules

Writes must be conservative.

Allowed early write operations:

create page
append to page end
append under a heading
append to journal
ensure journal exists

Avoid:

broad rewrites
reformatting entire documents
arbitrary reordering
risky transformations

Write features should support:

--dry-run
--backup
--backup-dir
--no-backup

Recommended write flow:

read original file
parse and validate
generate new content
compare diff
write atomically through a temp file + replace
11. Parsing requirements
Markdown first

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
Org early support

Org support can be limited in early versions:

heading
TODO
tags
scheduled
deadline
basic text

Org write support may be omitted or limited early.

12. Page resolution rules

When resolving page names, try in this order:

exact filename
case-insensitive filename
normalized match across spaces / underscores / hyphens
first heading title
page property title

Support Chinese filenames and titles.

13. Architecture expectations

Prefer this structure:

src/logseq_cli/
  cli/
  core/
  utils/
tests/
  fixtures/
docs/

Guidelines:

CLI modules should mostly parse args and call core functions
parsing/search/writer/task logic belongs in core/
errors should be centralized
models should be typed and reusable
avoid giant monolithic files

Suggested internal models:

Graph
Document
Block
SearchHit
TaskItem / TaskSummary
14. Testing expectations

Tests are required.

At minimum cover:

graph detection
page resolution
markdown block parsing
task extraction
page ref extraction
text search
append behavior

Use fixtures with:

multiple pages
multiple journals
nested blocks
TODO states
tags
page refs
scheduled/deadline dates
Chinese page names
ambiguous page names

For JSON commands, include golden-style expectations where practical.

15. Documentation expectations

Keep documentation current while implementing.

At minimum maintain:

README.md
docs/design.md
docs/implement.md

README should include:

project purpose
install instructions
example commands
JSON output shape
write safety behavior
known limitations

Do not document commands as available unless they are implemented.

16. Working style

Before editing:

inspect the repository
inspect docs/design.md and docs/implement.md
keep changes scoped to the current milestone

While editing:

implement incrementally
run tests after meaningful changes
update docs when behavior changes
do not stop after writing only plans
do not drift into unrelated cleanup

When done:

report what changed
report what is still missing
report exact test commands run
report example commands to verify behavior manually
17. Definition of done for MVP

MVP is done when:

graph detect works
page read works
page list works
journal read works
journal append works safely
search text works
tasks list works
all above support --json
tests cover core paths
README explains installation and usage