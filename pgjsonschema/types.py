"""Shared type definitions for structured JSON."""

from collections.abc import Mapping, Sequence
from typing import TypeAlias

JSONType: TypeAlias = (
    Mapping[str, "JSONType"] | Sequence["JSONType"] | str | int | float | bool | None
)
