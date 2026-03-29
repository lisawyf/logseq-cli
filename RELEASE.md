# Release Prep

This project is currently prepared for an initial `0.1.0` local release.

## Pre-release checks

Run these before publishing:

```bash
pytest
logseq-cli --help
python3 -m build --sdist --wheel
```

If isolated build environments cannot reach package indexes in your local setup, use:

```bash
python3 -m build --sdist --wheel --no-isolation
```

Optional smoke checks:

```bash
logseq-cli graph detect --graph tests/fixtures/sample_graph --json
logseq-cli page list --graph tests/fixtures/sample_graph --json
logseq-cli journal read --graph tests/fixtures/sample_graph --date 2026-03-29 --json
logseq-cli search text OpenClaw --graph tests/fixtures/sample_graph --json
logseq-cli search tags ops --graph tests/fixtures/sample_graph --json
```

## Release artifacts

Expected local artifacts after build:

- `dist/logseq_cli-0.1.0.tar.gz`
- `dist/logseq_cli-0.1.0-py3-none-any.whl`

## Notes

- This tool is intentionally CLI-only and local-file-based.
- Do not publish documentation that claims MCP, HTTP, daemon, or remote interfaces.
- Keep the documented command surface aligned with the actual implementation in `README.md`.
