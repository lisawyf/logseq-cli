from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class ErrorInfo(BaseModel):
    code: str
    message: str


class Graph(BaseModel):
    root: Path
    pages_dir: Path
    journals_dir: Path
    assets_dir: Path | None = None
    logseq_dir: Path | None = None
    config_path: Path | None = None


class Block(BaseModel):
    line_no: int
    type: Literal["bullet", "heading", "paragraph"]
    raw: str
    text: str
    indent: int = 0
    level: int | None = None
    parent_line_no: int | None = None
    todo_state: str | None = None
    tags: list[str] = Field(default_factory=list)
    page_refs: list[str] = Field(default_factory=list)
    scheduled: date | None = None
    deadline: date | None = None


class Document(BaseModel):
    name: str
    title: str
    path: Path
    doc_type: Literal["page", "journal"]
    format: Literal["markdown", "org"]
    content: str
    blocks: list[Block] = Field(default_factory=list)
    is_journal: bool = False
    journal_date: date | None = None


class SearchHit(BaseModel):
    path: Path
    title: str
    doc_type: Literal["page", "journal"]
    line_no: int
    snippet: str
    match_text: str


class TaskItem(BaseModel):
    path: Path
    title: str
    doc_type: Literal["page", "journal"]
    line_no: int
    state: str
    text: str
    tags: list[str] = Field(default_factory=list)
    page_refs: list[str] = Field(default_factory=list)
    scheduled: date | None = None
    deadline: date | None = None


class CommandResult(BaseModel):
    ok: bool
    command: str
    graph_root: str | None
    data: object | None
    warnings: list[str] = Field(default_factory=list)
    errors: list[ErrorInfo] = Field(default_factory=list)
