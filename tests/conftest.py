from __future__ import annotations

from pathlib import Path
import sys

import pytest
from typer.testing import CliRunner

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from logseq_cli.cli.app import app


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def fixture_graph() -> Path:
    return Path(__file__).parent / "fixtures" / "sample_graph"


@pytest.fixture(autouse=True)
def isolated_config_path(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("LOGSEQ_CLI_CONFIG_PATH", str(tmp_path / "config.toml"))
