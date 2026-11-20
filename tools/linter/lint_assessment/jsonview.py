"""Total accessors over parsed JSON.

Parsed JSON is `JsonValue`. Every real document is *mostly* the shape the writer intended
and *partly* something else, so every accessor here is total: it returns the value or `None`,
and it never raises on a wrong shape. A rule therefore reads a document as a sequence of
guarded questions —

    questions = get_array(assessment, "sections")
    if questions is None:
        yield error("identity", "$.assessment.sections", "sections is not an array")
        return

— instead of indexing hopefully and catching `KeyError` afterwards.
"""
from __future__ import annotations

from typing import TypeAlias

JsonValue: TypeAlias = "None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]"
JsonObject: TypeAlias = dict[str, JsonValue]
JsonArray: TypeAlias = list[JsonValue]


def as_object(value: JsonValue) -> JsonObject | None:
    """Requires: nothing. Ensures: the value if it is a JSON object, else `None`."""
    return value if isinstance(value, dict) else None


def as_array(value: JsonValue) -> JsonArray | None:
    """Requires: nothing. Ensures: the value if it is a JSON array, else `None`."""
    return value if isinstance(value, list) else None


def as_str(value: JsonValue) -> str | None:
    """Requires: nothing. Ensures: the value if it is a string, else `None`."""
    return value if isinstance(value, str) else None


def as_int(value: JsonValue) -> int | None:
    """Requires: nothing.

    Ensures: the value if it is an integer, else `None`. `True` and `False` are not
    integers here even though Python makes them `int` subclasses — a JSON `true` is not a
    count, and a linter that accepted it would let `"choose_n": true` through.
    """
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def get(obj: JsonObject, key: str) -> JsonValue:
    """Requires: `obj` is a JSON object. Ensures: `obj[key]`, or `None` when absent."""
    return obj.get(key)


def get_object(obj: JsonObject, key: str) -> JsonObject | None:
    """Requires: `obj` is a JSON object.

    Ensures: the member as an object, or `None` when absent or of another type.
    """
    return as_object(obj.get(key))


def get_array(obj: JsonObject, key: str) -> JsonArray | None:
    """Requires: `obj` is a JSON object.

    Ensures: the member as an array, or `None` when absent or of another type.
    """
    return as_array(obj.get(key))


def get_str(obj: JsonObject, key: str) -> str | None:
    """Requires: `obj` is a JSON object.

    Ensures: the member as a string, or `None` when absent or of another type.
    """
    return as_str(obj.get(key))


def get_int(obj: JsonObject, key: str) -> int | None:
    """Requires: `obj` is a JSON object.

    Ensures: the member as an integer (§see `as_int`), or `None` when absent or of another
    type.
    """
    return as_int(obj.get(key))


def objects(items: JsonArray) -> tuple[JsonObject, ...]:
    """Requires: `items` is a JSON array.

    Ensures: the members that are objects, in order. Non-object members are dropped here;
    the rule that owns the array is responsible for reporting them.
    """
    return tuple(o for o in (as_object(item) for item in items) if o is not None)
