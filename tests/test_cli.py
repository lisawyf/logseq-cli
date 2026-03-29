from __future__ import annotations

from pathlib import Path

from logseq_cli.cli.app import app


def test_graph_detect_json(runner, fixture_graph: Path) -> None:
    result = runner.invoke(app, ["graph", "detect", "--graph", str(fixture_graph), "--json"])

    assert result.exit_code == 0
    assert '"ok": true' in result.stdout
    assert str(fixture_graph.resolve()) in result.stdout


def test_graph_detect_autodiscovery(runner, fixture_graph: Path, monkeypatch) -> None:
    monkeypatch.chdir(fixture_graph / "pages")

    result = runner.invoke(app, ["graph", "detect"])

    assert result.exit_code == 0
    assert result.stdout.strip() == str(fixture_graph.resolve())


def test_graph_stats_json(runner, fixture_graph: Path) -> None:
    result = runner.invoke(app, ["graph", "stats", "--graph", str(fixture_graph), "--json"])

    assert result.exit_code == 0
    assert '"pages": 3' in result.stdout
    assert '"journals": 1' in result.stdout
    assert '"documents": 4' in result.stdout
    assert '"org_documents": 1' in result.stdout
    assert '"tasks": 7' in result.stdout


def test_page_list_json(runner, fixture_graph: Path) -> None:
    result = runner.invoke(app, ["page", "list", "--graph", str(fixture_graph), "--json"])

    assert result.exit_code == 0
    assert '"count": 3' in result.stdout
    assert '"title": "OpenClaw"' in result.stdout
    assert '"title": "Project Notes"' in result.stdout


def test_page_read_resolves_by_heading_title(runner, fixture_graph: Path) -> None:
    result = runner.invoke(
        app,
        ["page", "read", "Project Notes", "--graph", str(fixture_graph), "--json"],
    )

    assert result.exit_code == 0
    assert '"title": "Project Notes"' in result.stdout
    assert '"format": "org"' in result.stdout


def test_page_create_json(runner, tmp_path: Path) -> None:
    graph = tmp_path / "graph"
    (graph / "pages").mkdir(parents=True)
    (graph / "journals").mkdir()
    (graph / "logseq").mkdir()
    (graph / "logseq" / "config.edn").write_text("{}", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "page",
            "create",
            "New Page",
            "--graph",
            str(graph),
            "--text",
            "- TODO Start page",
            "--json",
        ],
    )

    created_page = graph / "pages" / "New Page.md"
    assert result.exit_code == 0
    assert '"command": "page create"' in result.stdout
    assert created_page.read_text(encoding="utf-8") == "# New Page\n\n- TODO Start page\n"


def test_page_create_dry_run_does_not_write(runner, tmp_path: Path) -> None:
    graph = tmp_path / "graph"
    (graph / "pages").mkdir(parents=True)
    (graph / "journals").mkdir()
    (graph / "logseq").mkdir()
    (graph / "logseq" / "config.edn").write_text("{}", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "page",
            "create",
            "Dry Run Page",
            "--graph",
            str(graph),
            "--dry-run",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert '"dry_run": true' in result.stdout
    assert not (graph / "pages" / "Dry Run Page.md").exists()


def test_page_create_rejects_existing_normalized_name(runner, fixture_graph: Path) -> None:
    result = runner.invoke(
        app,
        [
            "page",
            "create",
            "gateway health",
            "--graph",
            str(fixture_graph),
            "--json",
        ],
    )

    assert result.exit_code == 5
    assert '"code": "PAGE_ALREADY_EXISTS"' in result.stdout


def test_page_append_json(runner, tmp_path: Path) -> None:
    graph = tmp_path / "graph"
    (graph / "pages").mkdir(parents=True)
    (graph / "journals").mkdir()
    (graph / "logseq").mkdir()
    (graph / "logseq" / "config.edn").write_text("{}", encoding="utf-8")
    page_path = graph / "pages" / "Append Target.md"
    page_path.write_text("# Append Target\n", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "page",
            "append",
            "Append Target",
            "--graph",
            str(graph),
            "--text",
            "- Follow-up item",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert '"command": "page append"' in result.stdout
    assert page_path.read_text(encoding="utf-8") == "# Append Target\n- Follow-up item\n"


def test_page_append_dry_run_does_not_write(runner, tmp_path: Path) -> None:
    graph = tmp_path / "graph"
    (graph / "pages").mkdir(parents=True)
    (graph / "journals").mkdir()
    (graph / "logseq").mkdir()
    (graph / "logseq" / "config.edn").write_text("{}", encoding="utf-8")
    page_path = graph / "pages" / "Append Dry Run.md"
    page_path.write_text("# Append Dry Run\n", encoding="utf-8")
    before = page_path.read_text(encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "page",
            "append",
            "Append Dry Run",
            "--graph",
            str(graph),
            "--text",
            "- Preview item",
            "--dry-run",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert '"dry_run": true' in result.stdout
    assert page_path.read_text(encoding="utf-8") == before


def test_page_append_under_json(runner, tmp_path: Path) -> None:
    graph = tmp_path / "graph"
    (graph / "pages").mkdir(parents=True)
    (graph / "journals").mkdir()
    (graph / "logseq").mkdir()
    (graph / "logseq" / "config.edn").write_text("{}", encoding="utf-8")
    page_path = graph / "pages" / "Sectioned.md"
    page_path.write_text("# Sectioned\n\n## Alpha\n- first\n\n## Beta\n- second\n", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "page",
            "append-under",
            "Sectioned",
            "--graph",
            str(graph),
            "--heading",
            "Alpha",
            "--text",
            "- inserted",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert '"command": "page append-under"' in result.stdout
    assert page_path.read_text(encoding="utf-8") == "# Sectioned\n\n## Alpha\n- first\n\n- inserted\n## Beta\n- second\n"


def test_page_append_under_missing_heading_returns_error(runner, tmp_path: Path) -> None:
    graph = tmp_path / "graph"
    (graph / "pages").mkdir(parents=True)
    (graph / "journals").mkdir()
    (graph / "logseq").mkdir()
    (graph / "logseq" / "config.edn").write_text("{}", encoding="utf-8")
    page_path = graph / "pages" / "Sectioned.md"
    page_path.write_text("# Sectioned\n\n## Alpha\n- first\n", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "page",
            "append-under",
            "Sectioned",
            "--graph",
            str(graph),
            "--heading",
            "Missing",
            "--text",
            "- inserted",
            "--json",
        ],
    )

    assert result.exit_code == 4
    assert '"code": "HEADING_NOT_FOUND"' in result.stdout
    assert page_path.read_text(encoding="utf-8") == "# Sectioned\n\n## Alpha\n- first\n"


def test_journal_read_json(runner, fixture_graph: Path) -> None:
    result = runner.invoke(
        app,
        ["journal", "read", "--graph", str(fixture_graph), "--date", "2026-03-29", "--json"],
    )

    assert result.exit_code == 0
    assert '"journal_date": "2026-03-29"' in result.stdout
    assert "Prepare status update" in result.stdout


def test_journal_list_json(runner, tmp_path: Path) -> None:
    graph = tmp_path / "graph"
    (graph / "pages").mkdir(parents=True)
    (graph / "journals").mkdir()
    (graph / "logseq").mkdir()
    (graph / "logseq" / "config.edn").write_text("{}", encoding="utf-8")
    (graph / "journals" / "2026_03_28.md").write_text("- older\n", encoding="utf-8")
    (graph / "journals" / "2026_03_30.md").write_text("- newer\n", encoding="utf-8")
    (graph / "journals" / "2026_03_29.org").write_text("* Midpoint\n", encoding="utf-8")

    result = runner.invoke(
        app,
        ["journal", "list", "--graph", str(graph), "--json"],
    )

    assert result.exit_code == 0
    assert '"command": "journal list"' in result.stdout
    assert '"count": 3' in result.stdout
    assert result.stdout.index('"journal_date": "2026-03-30"') < result.stdout.index('"journal_date": "2026-03-29"')
    assert result.stdout.index('"journal_date": "2026-03-29"') < result.stdout.index('"journal_date": "2026-03-28"')


def test_journal_list_limit(runner, tmp_path: Path) -> None:
    graph = tmp_path / "graph"
    (graph / "pages").mkdir(parents=True)
    (graph / "journals").mkdir()
    (graph / "logseq").mkdir()
    (graph / "logseq" / "config.edn").write_text("{}", encoding="utf-8")
    (graph / "journals" / "2026_03_28.md").write_text("- older\n", encoding="utf-8")
    (graph / "journals" / "2026_03_30.md").write_text("- newer\n", encoding="utf-8")

    result = runner.invoke(
        app,
        ["journal", "list", "--graph", str(graph), "--limit", "1", "--json"],
    )

    assert result.exit_code == 0
    assert '"count": 1' in result.stdout
    assert '"journal_date": "2026-03-30"' in result.stdout


def test_journal_read_uses_iso_date_title(runner, fixture_graph: Path) -> None:
    result = runner.invoke(
        app,
        ["journal", "read", "--graph", str(fixture_graph), "--date", "2026-03-29", "--json"],
    )

    assert result.exit_code == 0
    assert '"title": "2026-03-29"' in result.stdout


def test_journal_ensure_creates_missing_file(runner, tmp_path: Path) -> None:
    graph = tmp_path / "graph"
    (graph / "pages").mkdir(parents=True)
    (graph / "journals").mkdir()
    (graph / "logseq").mkdir()
    (graph / "logseq" / "config.edn").write_text("{}", encoding="utf-8")

    result = runner.invoke(
        app,
        ["journal", "ensure", "--graph", str(graph), "--date", "2026-03-31", "--json"],
    )

    created_path = graph / "journals" / "2026_03_31.md"
    assert result.exit_code == 0
    assert '"command": "journal ensure"' in result.stdout
    assert '"created": true' in result.stdout
    assert created_path.exists()
    assert created_path.read_text(encoding="utf-8") == ""


def test_journal_ensure_dry_run_does_not_write(runner, tmp_path: Path) -> None:
    graph = tmp_path / "graph"
    (graph / "pages").mkdir(parents=True)
    (graph / "journals").mkdir()
    (graph / "logseq").mkdir()
    (graph / "logseq" / "config.edn").write_text("{}", encoding="utf-8")

    result = runner.invoke(
        app,
        ["journal", "ensure", "--graph", str(graph), "--date", "2026-03-31", "--dry-run", "--json"],
    )

    assert result.exit_code == 0
    assert '"dry_run": true' in result.stdout
    assert not (graph / "journals" / "2026_03_31.md").exists()


def test_journal_ensure_returns_existing_file(runner, fixture_graph: Path) -> None:
    result = runner.invoke(
        app,
        ["journal", "ensure", "--graph", str(fixture_graph), "--date", "2026-03-29", "--json"],
    )

    assert result.exit_code == 0
    assert '"created": false' in result.stdout
    assert '"date": "2026-03-29"' in result.stdout


def test_journal_summarize_json(runner, fixture_graph: Path) -> None:
    result = runner.invoke(
        app,
        ["journal", "summarize", "--graph", str(fixture_graph), "--date", "2026-03-29", "--json"],
    )

    assert result.exit_code == 0
    assert '"command": "journal summarize"' in result.stdout
    assert '"journal_date": "2026-03-29"' in result.stdout
    assert '"block_count": 2' in result.stdout
    assert '"task_count": 1' in result.stdout
    assert '"OpenClaw"' in result.stdout
    assert '"work"' in result.stdout


def test_search_text_json(runner, fixture_graph: Path) -> None:
    result = runner.invoke(
        app,
        ["search", "text", "OpenClaw", "--graph", str(fixture_graph), "--json"],
    )

    assert result.exit_code == 0
    assert '"query": "OpenClaw"' in result.stdout
    assert '"count":' in result.stdout
    assert "deployment notes" in result.stdout


def test_links_backlinks_json(runner, fixture_graph: Path) -> None:
    result = runner.invoke(
        app,
        ["links", "backlinks", "OpenClaw", "--graph", str(fixture_graph), "--json"],
    )

    assert result.exit_code == 0
    assert '"command": "links backlinks"' in result.stdout
    assert '"count": 1' in result.stdout
    assert '"title": "2026-03-29"' in result.stdout


def test_links_outgoing_json(runner, fixture_graph: Path) -> None:
    result = runner.invoke(
        app,
        ["links", "outgoing", "OpenClaw", "--graph", str(fixture_graph), "--json"],
    )

    assert result.exit_code == 0
    assert '"command": "links outgoing"' in result.stdout
    assert '"count": 2' in result.stdout
    assert '"page": "Gateway Health"' in result.stdout
    assert '"page": "Project Notes"' in result.stdout


def test_capture_quick_json(runner, tmp_path: Path) -> None:
    graph = tmp_path / "graph"
    (graph / "pages").mkdir(parents=True)
    (graph / "journals").mkdir()
    (graph / "logseq").mkdir()
    (graph / "logseq" / "config.edn").write_text("{}", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "capture",
            "quick",
            "--graph",
            str(graph),
            "--date",
            "2026-04-01",
            "--text",
            "Captured item",
            "--json",
        ],
    )

    journal_path = graph / "journals" / "2026_04_01.md"
    assert result.exit_code == 0
    assert '"command": "capture quick"' in result.stdout
    assert journal_path.read_text(encoding="utf-8") == "- Captured item\n"


def test_tasks_list_state_filter(runner, fixture_graph: Path) -> None:
    result = runner.invoke(
        app,
        ["tasks", "list", "--graph", str(fixture_graph), "--state", "doing", "--json"],
    )

    assert result.exit_code == 0
    assert '"count": 1' in result.stdout
    assert '"state": "DOING"' in result.stdout
    assert '"state": "TODO"' not in result.stdout


def test_journal_append_dry_run_does_not_write(runner, fixture_graph: Path) -> None:
    journal_path = fixture_graph / "journals" / "2026_03_30.md"
    result = runner.invoke(
        app,
        [
            "journal",
            "append",
            "--graph",
            str(fixture_graph),
            "--date",
            "2026-03-30",
            "--text",
            "Plan next milestone",
            "--dry-run",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert '"dry_run": true' in result.stdout
    assert not journal_path.exists()


def test_journal_append_writes_new_file(runner, tmp_path: Path) -> None:
    graph = tmp_path / "graph"
    (graph / "pages").mkdir(parents=True)
    (graph / "journals").mkdir()
    (graph / "logseq").mkdir()
    (graph / "logseq" / "config.edn").write_text("{}", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "journal",
            "append",
            "--graph",
            str(graph),
            "--date",
            "2026-03-30",
            "--text",
            "Plan next milestone",
        ],
    )

    assert result.exit_code == 0
    assert "Appended to" in result.stdout
    assert (graph / "journals" / "2026_03_30.md").read_text(encoding="utf-8") == "- Plan next milestone\n"


def test_page_not_found_json_includes_graph_root(runner, fixture_graph: Path) -> None:
    result = runner.invoke(
        app,
        ["page", "read", "Missing Page", "--graph", str(fixture_graph), "--json"],
    )

    assert result.exit_code == 4
    assert '"graph_root":' in result.stdout
    assert str(fixture_graph.resolve()) in result.stdout


def test_search_invalid_scope_has_invalid_argument_exit_code(runner, fixture_graph: Path) -> None:
    result = runner.invoke(
        app,
        ["search", "text", "OpenClaw", "--graph", str(fixture_graph), "--scope", "pages,invalid", "--json"],
    )

    assert result.exit_code == 2
    assert '"code": "INVALID_SCOPE"' in result.stdout


def test_page_read_rejects_raw_and_json_together(runner, fixture_graph: Path) -> None:
    result = runner.invoke(
        app,
        ["page", "read", "OpenClaw", "--graph", str(fixture_graph), "--raw", "--json"],
    )

    assert result.exit_code == 2
    assert '"code": "INVALID_OUTPUT_MODE"' in result.stdout
