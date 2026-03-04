import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Callable, Dict, Optional


# ---------------------------------------------------------------------------
# Validation result
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ValidationResult:
    error: Optional[str] = None

_OK = ValidationResult()


# ---------------------------------------------------------------------------
# Primitive checks
# ---------------------------------------------------------------------------
def _is_str(v: Any) -> bool:
    return isinstance(v, str) and bool(v.strip())

def _is_date(v: Any) -> bool:
    if isinstance(v, (date, datetime)):
        return True
    try:
        datetime.fromisoformat(str(v))
        return True
    except (ValueError, TypeError):
        return False

def _is_bool(v: Any) -> bool:
    return isinstance(v, bool)

def _is_str_list(v: Any) -> bool:
    return isinstance(v, list) and all(isinstance(i, str) for i in v)

def _is_number_0_5(v: Any) -> bool:
    return isinstance(v, (int, float)) and 0 <= v <= 5

def _is_url_or_empty(v: Any) -> bool:
    if not isinstance(v, str):
        return False
    return v == "" or bool(re.match(r"https?://", v))

def _enum(*values: str) -> Callable[[Any], bool]:
    return lambda v: v in values


# ---------------------------------------------------------------------------
# FieldRule — a validator paired with its required flag and error message.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class FieldRule:
    check: Callable[[Any], bool]
    message: str
    required: bool = True

    def validate(self, value: Any) -> ValidationResult:
        if value is None:
            return ValidationResult(error="field is required") if self.required else _OK
        return _OK if self.check(value) else ValidationResult(error=self.message)


# ---------------------------------------------------------------------------
# Reusable rule instances  (required=True by default, _OPT suffix = optional)
# ---------------------------------------------------------------------------
_STR          = FieldRule(_is_str,          "must be a non-empty string")
_STR_OPT      = FieldRule(_is_str,          "must be a non-empty string",          required=False)
_DATE         = FieldRule(_is_date,         "must be a valid date")
_BOOL_OPT     = FieldRule(_is_bool,         "must be a boolean",                   required=False)
_STR_LIST     = FieldRule(_is_str_list,     "must be an array of strings")
_STR_LIST_OPT = FieldRule(_is_str_list,     "must be an array of strings",         required=False)
_PROGRESS     = FieldRule(_is_number_0_5,   "must be a number between 0 and 5")
_URL_OPT      = FieldRule(_is_url_or_empty, "must be a valid URL or empty string",  required=False)

# Valid status values — source of truth: references/STATUSES.md
_STATUS       = FieldRule(_enum("idea", "poc", "wip", "done"),
                           "must be one of: idea, poc, wip, done")


# ---------------------------------------------------------------------------
# Per-collection schemas.
# Every field defined in the Astro schema is listed:
#   - required=True  → field MUST be present and valid
#   - required=False → field is validated only when present
# ---------------------------------------------------------------------------
COLLECTION_SCHEMAS: Dict[str, Dict[str, FieldRule]] = {
    "bits": {
        "title":          _STR,
        "description":    _STR,
        "date":           _DATE,
        "draft":          _BOOL_OPT,
        "stack":          _STR_LIST,
        "status":         _STATUS,
        "progress":       _PROGRESS,
        "type":           _STR,
        "images":         _STR_LIST_OPT,
        "repository_url": _URL_OPT,
        "demo_url":       _URL_OPT,
    },
    "atoms": {
        "title":          _STR,
        "shortTitle":     _STR,
        "description":    _STR,
        "date":           _DATE,
        "draft":          _BOOL_OPT,
        "icon":           _STR,
        "stack":          _STR_LIST,
        "status":         _STATUS,
        "type":           _STR,
        "images":         _STR_LIST_OPT,
        "repository_url": _URL_OPT,
        "demo_url":       _URL_OPT,
    },
    "mind": {
        "title":          _STR,
        "description":    _STR,
        "date":           _DATE,
        "draft":          _BOOL_OPT,
        "tags":           _STR_LIST_OPT,
        "references":     _STR_LIST_OPT,
        "status":         _STATUS,
    },
}
