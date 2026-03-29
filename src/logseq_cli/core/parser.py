from __future__ import annotations

from datetime import date
import re
from pathlib import Path

from logseq_cli.core.models import Block

TODO_STATES = {
    "TODO",
    "DOING",
    "DONE",
    "WAITING",
    "NOW",
    "LATER",
    "CANCELED",
    "CANCELLED",
}

PAGE_REF_RE = re.compile(r"\[\[([^\]]+)\]\]")
TAG_RE = re.compile(r"(?<!\w)#([A-Za-z0-9][\w/-]*)")
SCHEDULED_RE = re.compile(r"\bSCHEDULED:\s*[<\[]?(\d{4}-\d{2}-\d{2})")
DEADLINE_RE = re.compile(r"\bDEADLINE:\s*[<\[]?(\d{4}-\d{2}-\d{2})")
MD_BULLET_RE = re.compile(r"^(\s*)[-*+]\s+(.*)$")
MD_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
ORG_HEADING_RE = re.compile(r"^(\*+)\s+(.*)$")


def parse_markdown_blocks(content: str) -> list[Block]:
    blocks: list[Block] = []
    stack: list[Block] = []
    current_block: Block | None = None

    for line_no, raw_line in enumerate(content.splitlines(), start=1):
        bullet_match = MD_BULLET_RE.match(raw_line)
        heading_match = MD_HEADING_RE.match(raw_line)

        if bullet_match:
            indent = len(bullet_match.group(1).replace("\t", "    "))
            text = bullet_match.group(2).strip()
            parent_line_no = None
            while stack and stack[-1].indent >= indent:
                stack.pop()
            if stack:
                parent_line_no = stack[-1].line_no
            block = build_block(
                line_no=line_no,
                raw=raw_line,
                text=text,
                block_type="bullet",
                indent=indent,
                parent_line_no=parent_line_no,
            )
            blocks.append(block)
            stack.append(block)
            current_block = block
            continue

        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2).strip()
            block = build_block(
                line_no=line_no,
                raw=raw_line,
                text=text,
                block_type="heading",
                indent=0,
                level=level,
            )
            blocks.append(block)
            stack.clear()
            current_block = block
            continue

        stripped = raw_line.strip()
        if stripped and current_block is not None:
            current_block.text = f"{current_block.text}\n{stripped}"
            current_block.raw = f"{current_block.raw}\n{raw_line}"
            enrich_block(current_block, stripped)
        elif stripped:
            block = build_block(
                line_no=line_no,
                raw=raw_line,
                text=stripped,
                block_type="paragraph",
            )
            blocks.append(block)
            current_block = block

    return blocks


def parse_org_blocks(content: str) -> list[Block]:
    blocks: list[Block] = []
    stack: list[Block] = []
    current_block: Block | None = None

    for line_no, raw_line in enumerate(content.splitlines(), start=1):
        heading_match = ORG_HEADING_RE.match(raw_line)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2).strip()
            parent_line_no = None
            while stack and (stack[-1].level or 0) >= level:
                stack.pop()
            if stack:
                parent_line_no = stack[-1].line_no
            block = build_block(
                line_no=line_no,
                raw=raw_line,
                text=text,
                block_type="heading",
                level=level,
                parent_line_no=parent_line_no,
            )
            blocks.append(block)
            stack.append(block)
            current_block = block
            continue

        stripped = raw_line.strip()
        if stripped and current_block is not None:
            current_block.text = f"{current_block.text}\n{stripped}"
            current_block.raw = f"{current_block.raw}\n{raw_line}"
            enrich_block(current_block, stripped)
        elif stripped:
            block = build_block(
                line_no=line_no,
                raw=raw_line,
                text=stripped,
                block_type="paragraph",
            )
            blocks.append(block)
            current_block = block

    return blocks


def parse_blocks(content: str, file_path: Path) -> list[Block]:
    if file_path.suffix.lower() == ".org":
        return parse_org_blocks(content)
    return parse_markdown_blocks(content)


def extract_title(content: str, file_path: Path) -> str:
    lines = content.splitlines()
    if file_path.suffix.lower() == ".org":
        for line in lines:
            match = ORG_HEADING_RE.match(line.strip())
            if match:
                text = strip_todo_prefix(match.group(2).strip())
                return strip_org_tags(text)
    else:
        for line in lines:
            match = MD_HEADING_RE.match(line.strip())
            if match and len(match.group(1)) == 1:
                return strip_todo_prefix(match.group(2).strip())
    return file_path.stem.replace("_", " ").replace("-", " ")


def extract_tags(text: str) -> list[str]:
    return sorted({match.group(1) for match in TAG_RE.finditer(text)})


def extract_page_refs(text: str) -> list[str]:
    return [match.group(1).strip() for match in PAGE_REF_RE.finditer(text)]


def extract_date_from_pattern(pattern: re.Pattern[str], text: str) -> date | None:
    match = pattern.search(text)
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(1))
    except ValueError:
        return None


def strip_todo_prefix(text: str) -> str:
    parts = text.split(maxsplit=1)
    if len(parts) == 2 and parts[0].upper() in TODO_STATES:
        return parts[1]
    return text


def strip_org_tags(text: str) -> str:
    if " :" not in text or not text.endswith(":"):
        return text
    body, _, maybe_tags = text.rpartition(" :")
    if maybe_tags and all(chunk for chunk in maybe_tags.split(":") if chunk):
        return body
    return text


def build_block(
    *,
    line_no: int,
    raw: str,
    text: str,
    block_type: str,
    indent: int = 0,
    level: int | None = None,
    parent_line_no: int | None = None,
) -> Block:
    todo_state, clean_text = split_todo_state(text)
    block = Block(
        line_no=line_no,
        type=block_type,
        raw=raw,
        text=clean_text,
        indent=indent,
        level=level,
        parent_line_no=parent_line_no,
        todo_state=todo_state,
    )
    enrich_block(block, clean_text)
    return block


def split_todo_state(text: str) -> tuple[str | None, str]:
    parts = text.split(maxsplit=1)
    if len(parts) == 2 and parts[0].upper() in TODO_STATES:
        return parts[0].upper(), parts[1]
    return None, text


def enrich_block(block: Block, text: str) -> None:
    block.tags = sorted(set(block.tags).union(extract_tags(text)))
    block.page_refs = list(dict.fromkeys(block.page_refs + extract_page_refs(text)))
    block.scheduled = block.scheduled or extract_date_from_pattern(SCHEDULED_RE, text)
    block.deadline = block.deadline or extract_date_from_pattern(DEADLINE_RE, text)
