# implement.md

This file defines the implementation sequence.

Read this file together with:
- `AGENTS.md`
- `docs/design.md`

`AGENTS.md` defines repository rules.
`design.md` defines product and architecture intent.
This file defines the execution order.

---

## 1. Mission

Implement a Python CLI named `logseq-cli` for **file-based Logseq graphs**.

This is a **local CLI only** project.

Do not implement:
- MCP
- HTTP server mode
- daemon mode
- network APIs
- any remote interface

Focus on:
- local file access
- Markdown-first correctness
- safe append-oriented writes
- stable `--json` output
- tests and documentation

---

## 2. Execution rules

- Keep changes scoped to the current milestone.
- Do not introduce unrelated cleanup.
- Reuse existing code when it fits the design.
- Prefer small, verifiable steps.
- Run tests after meaningful changes.
- Update README when behavior changes.
- If a feature is too large, implement the safe subset first and document limitations.
- Do not claim support for commands that are not implemented.

---

## 3. Milestone order

### Milestone 0: Inspect repository
Before coding:

- inspect repository layout
- inspect `pyproject.toml`
- inspect existing source code
- inspect tests
- inspect `AGENTS.md`
- inspect `docs/design.md`

Determine:
- what already exists
- what can be reused
- what is missing

Do not rewrite working code without reason.

---

### Milestone 1: Project skeleton
Ensure the project has:

- `src/logseq_cli/__init__.py`
- `src/logseq_cli/main.py`
- `src/logseq_cli/cli/`
- `src/logseq_cli/core/`
- `src/logseq_cli/utils/`
- `tests/fixtures/`

Requirements:
- `logseq-cli --help` must run
- basic Typer app structure must exist
- package import path must work
- tests must be runnable

Validation:
- run `logseq-cli --help`
- run `pytest`

---

### Milestone 2: Core models and graph detection
Implement typed internal models for at least:

- Graph
- Document
- Block
- SearchHit
- TaskItem

Implement:
- graph root discovery
- graph validation
- `graph detect`

Support:
- explicit `--graph`
- auto-discovery from current directory upward
- optional config-based default graph if straightforward

Validation:
- add graph detection tests
- verify JSON output shape
- verify error behavior when graph is missing

---

### Milestone 3: Markdown parser MVP
Implement Markdown parsing for common Logseq-like constructs:

- bullet/list blocks
- nesting by indentation
- TODO states
- page refs
- tags
- headings
- scheduled/deadline extraction
- common block text extraction

Do not overreach for perfect syntax support.

Validation:
- parser unit tests
- fixture coverage for nested blocks, refs, tasks, tags, and dates

---

### Milestone 4: Page and journal reads
Implement:

- `page read`
- `page list`
- `journal read`

Support:
- text output
- `--json`
- `--raw` where useful

Requirements:
- page name resolution rules from `design.md`
- stable JSON envelope

Validation:
- tests for page resolution
- tests for page read and journal read
- manual examples in README

---

### Milestone 5: Text search MVP
Implement:

- `search text`

Support:
- keyword search
- scope filtering if practical
- limit
- snippets/context
- `--json`

Time-based filtering is optional in MVP if it complicates core correctness.

Validation:
- search tests
- verify search results against fixtures

---

### Milestone 6: Task extraction MVP
Implement:

- task extraction from parsed blocks
- `tasks list`

Support:
- TODO-state recognition
- JSON output
- basic state filtering if practical

Validation:
- task extraction tests
- command-level tests

---

### Milestone 7: Safe journal append MVP
Implement:

- `journal append`

Support:
- `--today`
- `--date`
- `--text`
- `--dry-run`

If practical, also support:
- backups
- backup directory selection

Requirements:
- append should be conservative
- avoid broad rewrites
- use predictable output
- keep implementation easy to reason about

Validation:
- append tests
- verify dry-run behavior
- verify append-only style behavior

---

### Milestone 8: README alignment
Update `README.md` so it matches actual implementation.

README must accurately describe:
- what commands are implemented
- how to install
- how to run tests
- sample commands
- JSON output shape
- known limitations

Do not document unimplemented commands as available.

---

## 4. MVP completion checklist

The MVP is complete only when all are true:

- `graph detect` works
- `page read` works
- `page list` works
- `journal read` works
- `journal append` works safely
- `search text` works
- `tasks list` works
- all of the above support `--json`
- tests cover the main logic
- README reflects actual behavior

---

## 5. Post-MVP order

After MVP is stable, implement these in order:

1. `graph stats`
2. `page create`
3. `page append`
4. `page append-under`
5. `journal list`
6. `journal ensure`
7. `links backlinks`
8. `links outgoing`
9. `journal summarize`
10. `capture quick`
11. `capture project`
12. `capture task`
13. `summarize daily`
14. `summarize weekly`
15. `summarize project`
16. `summarize topic`
17. `search links`
18. `search tags`

Only move beyond MVP if MVP is already reliable.

---

## 6. Verification commands

Run as many of these as apply:

```bash
pytest
logseq-cli --help
logseq-cli graph detect --graph tests/fixtures/sample_graph
logseq-cli page list --graph tests/fixtures/sample_graph --json
logseq-cli page read "OpenClaw" --graph tests/fixtures/sample_graph --json
logseq-cli journal read --date 2026-03-29 --graph tests/fixtures/sample_graph --json
logseq-cli search text "OpenClaw" --graph tests/fixtures/sample_graph --json
logseq-cli tasks list --graph tests/fixtures/sample_graph --json

For append validation:

logseq-cli journal append --date 2026-03-29 --graph tests/fixtures/sample_graph --text "test append" --dry-run

If a command is not implemented, do not pretend it is available.
Document the gap clearly.

7. Final response requirements

At the end of implementation, report:

what was implemented
what remains
what files changed
what tests were run
what manual commands can be used to verify behavior
what limitations are known

Keep the report concrete.