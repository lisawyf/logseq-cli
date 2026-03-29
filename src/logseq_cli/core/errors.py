from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class LogseqCliError(Exception):
    code: str
    message: str
    exit_code: int

    def __str__(self) -> str:
        return self.message


class ExitCodes:
    SUCCESS = 0
    GENERAL_FAILURE = 1
    INVALID_ARGUMENTS = 2
    GRAPH_NOT_FOUND = 3
    PAGE_NOT_FOUND = 4
    WRITE_CONFLICT = 5
    PARSE_FAILURE = 6

