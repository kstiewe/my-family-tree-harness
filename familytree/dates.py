"""Genealogical dates: exact, about (~), before (<), after (>) and between (a..b)."""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass

from .i18n import fmt_ymd, tr

TODAY = dt.date.today()
MONTHS_GED = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()
_YMD = re.compile(r"^(\d{3,4})(?:-(\d{1,2})(?:-(\d{1,2}))?)?$")
YMD = tuple[int, "int | None", "int | None"]


def _ymd(text: str) -> YMD | None:
    m = _YMD.match(text.strip())
    if not m:
        return None
    y, mo, d = int(m[1]), m[2] and int(m[2]), m[3] and int(m[3])
    if mo is not None and not 1 <= mo <= 12:
        return None
    if d is not None:
        try:
            dt.date(y, mo, d)
        except ValueError:
            return None
    return (y, mo, d)


def sort_key(t: YMD) -> tuple[int, int, int]:
    return (t[0], t[1] or 0, t[2] or 0)


@dataclass(frozen=True)
class Date:
    """A date with a qualifier: exact | about | before | after | between."""
    raw: str
    kind: str
    a: YMD
    b: YMD | None = None

    @property
    def year(self) -> int:
        return (self.a[0] + self.b[0]) // 2 if self.kind == "between" else self.a[0]

    @property
    def bounds(self) -> tuple[int | None, int | None]:
        y = self.a[0]
        return {"exact": (y, y), "about": (y - 2, y + 2), "before": (None, y), "after": (y, None),
                "between": (y, self.b[0] if self.b else y)}[self.kind]

    @property
    def precise(self) -> bool:
        return self.kind in ("exact", "about") or (self.kind == "between" and self.b[0] - self.a[0] <= 5)

    def ged(self) -> str:
        def one(t: YMD) -> str:
            y, m, d = t
            return " ".join(([str(d)] if d else []) + ([MONTHS_GED[m - 1]] if m else []) + [str(y)])
        return {"exact": one(self.a), "about": f"ABT {one(self.a)}", "before": f"BEF {one(self.a)}",
                "after": f"AFT {one(self.a)}", "between": f"BET {one(self.a)} AND {one(self.b or self.a)}"}[self.kind]

    def text(self) -> str:
        """Human-readable form in the active language."""
        one = lambda t: fmt_ymd(*t)
        if self.kind == "exact":
            return one(self.a)
        if self.kind == "between":
            return f"{one(self.a)}–{one(self.b or self.a)}"
        return tr({"about": "c. {date}", "before": "before {date}", "after": "after {date}"}[self.kind], date=one(self.a))


def parse_date(raw) -> Date | None:
    if raw is None:
        return None
    if isinstance(raw, dt.date):
        raw = raw.isoformat()
    s = str(raw).strip()
    if s in ("", "?"):
        return None
    if ".." in s:
        a, b = (_ymd(x) for x in s.split("..", 1))
        if a and b and a[0] <= b[0]:
            return Date(s, "between", a, b)
        raise ValueError(tr('invalid date range {value!r} (pattern: "1848..1852")', value=s))
    kind = {"~": "about", "<": "before", ">": "after"}.get(s[0], "exact")
    a = _ymd(s if kind == "exact" else s[1:])
    if not a:
        raise ValueError(tr('invalid date {value!r} (patterns: "1850-03-12", "1850", "~1850", "<1870", ">1845")', value=s))
    return Date(s, kind, a)


def safe_date(raw) -> Date | None:
    try:
        return parse_date(raw)
    except ValueError:
        return None


@dataclass
class Window:
    """Estimated range of years (e.g. of birth) with the evidence behind it."""
    lo: int | None
    hi: int | None
    basis: list[str]
    conflict: bool = False

    def text(self) -> str:
        if self.lo is not None and self.hi is not None:
            return str(self.lo) if self.lo == self.hi else f"{self.lo}–{self.hi}"
        if self.lo is not None:
            return tr("after {date}", date=self.lo)
        return tr("before {date}", date=self.hi) if self.hi is not None else "?"


def search_range(lo: int | None, hi: int | None, pad: int = 1) -> tuple[int, int] | None:
    """Years to query: padded; an open end is closed at 40 years."""
    if lo is None and hi is None:
        return None
    lo = hi - 40 if lo is None else lo
    hi = lo + 40 if hi is None else hi
    return lo - pad, min(max(hi, lo) + pad, TODAY.year)
