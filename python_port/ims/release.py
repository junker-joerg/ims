"""Authoritative application release; independent of model/schema versions."""
from __future__ import annotations

import re

VERSION = "2.0.0-alpha.7"


def windows_file_version(version: str) -> str:
    """Map supported releases to an ordered four-part Windows file version."""
    number = r"(0|[1-9][0-9]*)"
    match = re.fullmatch(rf"{number}\.{number}\.{number}(?:-alpha\.{number})?", version)
    if match is None:
        raise ValueError("Use major.minor.patch or major.minor.patch-alpha.number")
    parts = tuple(int(value) for value in match.groups()[:3])
    revision = int(match[4]) if match[4] is not None else 65535
    if any(value > 65535 for value in parts) or not 0 <= revision <= 65535:
        raise ValueError("Windows version components must be between 0 and 65535")
    if match[4] is not None and revision == 65535:
        raise ValueError("Alpha revision 65535 is reserved for the final release")
    return ".".join(str(value) for value in (*parts, revision))


WINDOWS_FILE_VERSION = windows_file_version(VERSION)
