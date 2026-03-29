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


def test_journal_read_json(runner, fixture_graph: Path) -> None:
    result = runner.invoke(
        app,
        ["journal", "read", "--graph", str(fixture_graph), "--date", "2026-03-29", "--json"],
    )

    assert result.exit_code == 0
    assert '"journal_date": "2026-03-29"' in result.stdout
    assert "Prepare status update" in result.stdout


def test_search_text_json(runner, fixture_graph: Path) -> None:
    result = runner.invoke(
        app,
        ["search", "text", "OpenClaw", "--graph", str(fixture_graph), "--json"],
    )

    assert result.exit_code == 0
    assert '"query": "OpenClaw"' in result.stdout
    assert '"count":' in result.stdout
    assert "deployment notes" in result.stdout


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
