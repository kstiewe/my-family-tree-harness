"""User-facing language of the application.

Code, identifiers and message ids are English. `tr()` looks a message id up in the catalog of the
active language (`familytree/locales/<code>.py`) and falls back to the English id. Message ids
always go through `str.format`, so literal braces in an id must be doubled.

Templates (`familytree/templates/*.html`) mark translatable text as ⟦message id⟧; `fill()` swaps
it for the translation without formatting, because template text is JavaScript and CSS.
"""

from __future__ import annotations

import importlib
import os
import re

DEFAULT = "en"
ENV_VAR = "FAMILYTREE_LANG"
MONTHS_EN = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()

_lang = DEFAULT
_catalog: dict[str, str] = {}


def available() -> list[str]:
    from pathlib import Path
    names = [p.stem for p in (Path(__file__).parent / "locales").glob("*.py") if p.stem != "__init__"]
    return sorted({DEFAULT, *names})


def resolve(explicit: str | None = None, project: dict | None = None) -> str:
    """CLI flag > project.yaml `language` > FAMILYTREE_LANG > English."""
    for value in (explicit, (project or {}).get("language"), os.environ.get(ENV_VAR)):
        if value:
            return str(value).strip().lower()
    return DEFAULT


def set_language(code: str) -> str:
    """Activate a language; unknown codes fall back to English. Returns the active code."""
    global _lang, _catalog
    code = (code or DEFAULT).lower()
    if code == DEFAULT:
        _lang, _catalog = DEFAULT, {}
        return _lang
    try:
        module = importlib.import_module(f"familytree.locales.{code}")
    except ModuleNotFoundError:
        _lang, _catalog = DEFAULT, {}
        return _lang
    _lang, _catalog = code, dict(module.MESSAGES)
    return _lang


def language() -> str:
    return _lang


def lookup(msgid: str) -> str:
    return _catalog.get(msgid, msgid)


def tr(msgid: str, **kw) -> str:
    return lookup(msgid).format(**kw)


def fmt_ymd(y: int, m: int | None, d: int | None) -> str:
    """One calendar date in the local style (Polish: 12.03.1850, English: 12 Mar 1850)."""
    if _lang == "pl":
        return f"{d:02d}.{m:02d}.{y}" if d else f"{m:02d}.{y}" if m else str(y)
    return " ".join(([str(d)] if d else []) + ([MONTHS_EN[m - 1]] if m else []) + [str(y)])


_MARK = re.compile(r"⟦(.+?)⟧", re.S)


def fill(template: str) -> str:
    """Replace ⟦message id⟧ markers in a template with translations."""
    return _MARK.sub(lambda m: lookup(m.group(1)), template)


def template_ids(template: str) -> list[str]:
    return _MARK.findall(template)
