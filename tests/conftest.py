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
