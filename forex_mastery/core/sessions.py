"""
Forex trading sessions, computed correctly across daylight-saving changes.

WHY NOT JUST MEMORISE UTC TIMES?
--------------------------------
Because they move. London summer time (BST) starts and ends on different dates
than US daylight time (EDT), so for a few weeks each year the London-New York
overlap shifts by an hour relative to a naive "13:00-17:00 UTC" rule. Anyone
trading a session-based strategy with a hard-coded UTC window trades the wrong
hours twice a year.

HOW THIS MODULE SOLVES IT
-------------------------
Each session is defined by its **local exchange hours** plus an IANA time zone
name (``"Europe/London"``, ``"America/New_York"``, ``"Asia/Tokyo"``,
``"Australia/Sydney"``). ``zoneinfo`` (standard library since Python 3.9)
converts them to UTC for the date you ask about, applying that city's real
daylight-saving rules. No date arithmetic is hard-coded.

    Important caveat: **liquidity, not clocks, defines a session.** The tables
    here describe exchange hours and the well-documented general pattern of
    activity. They are not a guarantee that "London will be volatile today".

WHAT IS WELL ESTABLISHED vs WHAT IS FOLKLORE
--------------------------------------------
Established: the London-New York overlap (roughly 12:00-16:00 UTC in northern
summer, 13:00-17:00 UTC in northern winter) historically concentrates the
highest volume and tightest spreads on EUR/USD and GBP/USD, because both major
centres are open. The Asia-Pacific window is typically quieter and ranges more.

Folklore: "the London open always reverses the Asian range", "never trade the
Monday gap", "Friday 22:00 is when the market closes" (it is 22:00 UTC, which is
not the same as your local Friday evening). Test everything on your own data.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Iterable
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

__all__ = [
    "SESSION_DEFINITIONS",
    "SESSION_CHARACTERISTICS",
    "SessionWindow",
    "active_sessions",
    "current_overlaps",
    "format_session_table",
    "is_market_open",
    "next_session_open",
    "session_table",
    "session_window_utc",
]

# ---------------------------------------------------------------------- #
# Definitions: local exchange hours + IANA time zone
# ---------------------------------------------------------------------- #
SESSION_DEFINITIONS: dict[str, dict] = {
    "Sydney": {"tz": "Australia/Sydney", "open": (8, 0), "close": (17, 0), "order": 0},
    "Tokyo": {"tz": "Asia/Tokyo", "open": (9, 0), "close": (18, 0), "order": 1},
    "London": {"tz": "Europe/London", "open": (8, 0), "close": (17, 0), "order": 2},
    "New York": {"tz": "America/New_York", "open": (8, 0), "close": (17, 0), "order": 3},
}

# Descriptive notes only. Every claim here is a widely documented *tendency*,
# not a rule, and none of it is a trading signal.
SESSION_CHARACTERISTICS: dict[str, str] = {
    "Sydney": (
        "First session of the week to open. Thin liquidity, small ranges, wide relative spreads; "
        "primarily AUD and NZD pairs. Poor environment for breakout strategies; historically a "
        "range-forming session. Most retail traders are asleep and should stay asleep."
    ),
    "Tokyo": (
        "Asia's main session. JPY pairs (USDJPY, EURJPY, AUDJPY) most active. Wide but often "
        "orderly ranges; the Bank of Japan and Japanese data are released in this window. Ranges "
        "from the Asian session are commonly used by London traders as reference levels - which is "
        "why the Asian high/low is a level worth marking, not because of any hidden mechanism."
    ),
    "London": (
        "Highest-volume session for FX. Spreads on majors are tightest, ranges largest, and the "
        "session open frequently produces the day's initial expansion. Most European economic "
        "releases land here (roughly 08:00-10:00 local). Best liquidity for GBP, EUR and CHF pairs."
    ),
    "New York": (
        "US data releases (CPI, NFP, FOMC) land here, typically 08:30 and 14:00 local. The "
        "London-New York overlap is the most liquid window of the day; after London closes, "
        "activity decays into the afternoon and spreads widen again into the close."
    ),
    "London/New York overlap": (
        "Historically the most liquid and volatile window of the day, and typically the tightest "
        "spreads on majors. Also the window where US and European news can push price in opposite "
        "directions within minutes. Volatility here is an opportunity *only* if your strategy was "
        "tested in it."
    ),
    "Off-hours lull": (
        "Between the New York close and the Tokyo open, roughly 21:00-00:00 UTC (winter) or "
        "22:00-00:00 UTC (summer, when Tokyo resumes at 23:00-00:00 UTC). Liquidity is at its "
        "weekday low: spreads widen, ranges compress, and stop-losses get picked off cheaply. "
        "For a beginner this window is a NO-TRADE window by default."
    ),
}

_SESSION_ORDER = ("Sydney", "Tokyo", "London", "New York")


# ---------------------------------------------------------------------- #
# Window computation
# ---------------------------------------------------------------------- #
@dataclass(frozen=True)
class SessionWindow:
    """One session occurrence, expressed in UTC and in the exchange's local time."""

    name: str
    start_utc: dt.datetime
    end_utc: dt.datetime
    local_open: str
    local_close: str
    local_timezone: str

    @property
    def duration_hours(self) -> float:
        return (self.end_utc - self.start_utc).total_seconds() / 3600.0

    def contains(self, when: dt.datetime) -> bool:
        when = _as_utc(when)
        return self.start_utc <= when < self.end_utc

    def as_row(self, display_tz: str | None = None) -> dict[str, str]:
        tz = ZoneInfo(display_tz) if display_tz else dt.timezone.utc
        return {
            "session": self.name,
            "local_hours": f"{self.local_open}-{self.local_close} {self.local_timezone}",
            "utc_hours": f"{self.start_utc:%H:%M}-{self.end_utc:%H:%M}",
            "your_time": (
                f"{self.start_utc.astimezone(tz):%H:%M}-{self.end_utc.astimezone(tz):%H:%M}"
                f" {display_tz}"
            )
            if display_tz
            else "UTC",
            "duration_h": f"{self.duration_hours:.1f}",
        }


def _as_utc(when: dt.datetime) -> dt.datetime:
    """Normalise any datetime to timezone-aware UTC."""
    if when.tzinfo is None:
        return when.replace(tzinfo=dt.timezone.utc)
    return when.astimezone(dt.timezone.utc)


def _safe_zone(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError):  # pragma: no cover - depends on host tzdata
        raise RuntimeError(
            f"Time zone database entry {name!r} is unavailable. On Windows install `tzdata` "
            "(pip install tzdata) so daylight-saving calculations remain correct."
        ) from None


def session_window_utc(name: str, on_date: dt.date | dt.datetime) -> SessionWindow:
    """UTC window for one session on the exchange-local date ``on_date``.

    The local date is what the exchange experiences, so the returned UTC window
    may start on the previous calendar day (Sydney, for example).

    Example
    -------
    >>> import datetime as dt
    >>> w = session_window_utc("London", dt.date(2026, 1, 15))   # GMT, winter
    >>> (w.start_utc.hour, w.end_utc.hour)
    (8, 17)
    >>> w2 = session_window_utc("London", dt.date(2026, 7, 15))   # BST, summer
    >>> (w2.start_utc.hour, w2.end_utc.hour)
    (7, 16)
    """
    if name not in SESSION_DEFINITIONS:
        raise KeyError(f"Unknown session {name!r}. Known: {tuple(SESSION_DEFINITIONS)}")
    spec = SESSION_DEFINITIONS[name]
    zone = _safe_zone(spec["tz"])
    local_date = on_date.date() if isinstance(on_date, dt.datetime) else on_date
    open_h, open_m = spec["open"]
    close_h, close_m = spec["close"]
    local_open = dt.datetime.combine(local_date, dt.time(open_h, open_m), tzinfo=zone)
    local_close = dt.datetime.combine(local_date, dt.time(close_h, close_m), tzinfo=zone)
    return SessionWindow(
        name=name,
        start_utc=local_open.astimezone(dt.timezone.utc),
        end_utc=local_close.astimezone(dt.timezone.utc),
        local_open=f"{open_h:02d}:{open_m:02d}",
        local_close=f"{close_h:02d}:{close_m:02d}",
        local_timezone=spec["tz"],
    )


def _windows_around(when: dt.datetime) -> list[SessionWindow]:
    """All session windows for the days that could possibly contain ``when``."""
    when = _as_utc(when)
    windows: list[SessionWindow] = []
    for offset in (-1, 0, 1):
        day = (when + dt.timedelta(days=offset)).date()
        for name in _SESSION_ORDER:
            windows.append(session_window_utc(name, day))
    windows.sort(key=lambda w: w.start_utc)
    return windows


def active_sessions(when: dt.datetime) -> list[str]:
    """Names of the sessions open at ``when`` (empty list = market quiet/closed).

    Example
    -------
    >>> import datetime as dt
    >>> active_sessions(dt.datetime(2026, 1, 15, 14, 0, tzinfo=dt.timezone.utc))
    ['London', 'New York']
    """
    when = _as_utc(when)
    return [w.name for w in _windows_around(when) if w.contains(when)]


def current_overlaps(when: dt.datetime) -> list[str]:
    """Human-readable overlaps active at ``when`` (e.g. ``["London/New York"]``)."""
    active = [name for name in _SESSION_ORDER if name in active_sessions(when)]
    overlaps = []
    for i, first in enumerate(active):
        for second in active[i + 1:]:
            pair = f"{first}/{second}"
            overlaps.append("London/New York" if pair == "London/New York" else pair)
    return overlaps


def next_session_open(when: dt.datetime, session: str | None = None) -> SessionWindow:
    """The next window to open after ``when`` (optionally for one session)."""
    when = _as_utc(when)
    for window in _windows_around(when):
        if window.start_utc > when and (session is None or window.name == session):
            return window
    raise RuntimeError("No future session window found - this should be unreachable")


def session_table(on_date: dt.date | dt.datetime, display_tz: str | None = None) -> list[dict[str, str]]:
    """Timetable for one exchange-local date, with optional local-time column."""
    rows = [session_window_utc(name, on_date).as_row(display_tz) for name in _SESSION_ORDER]
    return rows


def format_session_table(on_date: dt.date | dt.datetime, display_tz: str | None = None) -> str:
    """Render :func:`session_table` as aligned text for the terminal or a journal."""
    rows = session_table(on_date, display_tz)
    headers = ["session", "local hours", "UTC hours", "your time"]
    keys = ["session", "local_hours", "utc_hours", "your_time"]
    cells = [[str(row.get(key, "")) for key in keys] for row in rows]
    widths = [
        max(len(headers[i]), *(len(row[i]) for row in cells)) + 2 if cells else len(headers[i]) + 2
        for i in range(len(headers))
    ]
    widths = [max(12, w) for w in widths]
    header = "".join(f"{headers[i]:<{widths[i]}}" for i in range(len(headers)))
    lines = ["=" * 78, f"FOREX SESSIONS - {on_date}", "=" * 78, header, "-" * 78]
    for row in cells:
        lines.append("".join(f"{row[i]:<{widths[i]}}" for i in range(len(headers))))
    lines.append("-" * 78)
    lines.append("  'local hours' = the exchange's own clock (this is what changes with DST).")
    lines.append("  'UTC hours'   = the same window converted to UTC (what your charts use).")
    lines.append("  Day-of-week matters: FX trades from Sunday 21:00 UTC to Friday 21:00 UTC,")
    lines.append("  and a Sunday 'Tokyo' window is really the Monday session opening early.")
    return "\n".join(lines)


def is_market_open(when: dt.datetime) -> bool:
    """Rough FX market open/closed test.

    The cash FX market runs continuously from about Sunday 21:00-22:00 UTC to
    Friday 21:00-22:00 UTC. Exact open and close times differ by broker (and by
    daylight saving), so treat this as a planning aid, not an execution rule:
    the authoritative answer is your platform's tick data.
    """
    when = _as_utc(when)
    weekday = when.weekday()  # Monday = 0 ... Sunday = 6
    if weekday == 5:  # Saturday
        return False
    if weekday == 6:  # Sunday: opens in the evening UTC
        return when.hour >= 21
    if weekday == 4:  # Friday: closes in the evening UTC
        return when.hour < 22
    return True


def is_low_liquidity_lull(when: dt.datetime) -> bool:
    """True in the thin window between the New York close and the Tokyo open.

    Roughly 21:00-00:00 UTC. Sydney is nominally open for part of it, which is
    exactly the trap this helper exists to avoid: **a session being open is not
    evidence of liquidity.** In this window spreads are at their widest relative
    to typical range and stop-runs are cheap to engineer, so the beginner rule
    is: no new positions.
    """
    when = _as_utc(when)
    if not is_market_open(when):
        return False
    return when.hour >= 21 or when.hour < 0  # 21:00-24:00 UTC (Sydney only, Tokyo shut)


def session_liquidity_rank(when: dt.datetime) -> dict[str, object]:
    """Ordinal liquidity/volatility context for scheduling decisions.

    Returns a dict with the active sessions, the overlap (if any), an ordinal
    ``liquidity_score`` in 1..4 (4 = densest window of the day) and the
    descriptive note. It is a **scheduling** helper, not a signal generator.
    """
    when = _as_utc(when)
    active = active_sessions(when)
    overlaps = current_overlaps(when)
    score = 1
    note = SESSION_CHARACTERISTICS["Off-hours lull"]
    if "Tokyo" in active and "London" not in active:
        score, note = 2, SESSION_CHARACTERISTICS["Tokyo"]
    if "London" in active and "New York" not in active:
        score, note = 3, SESSION_CHARACTERISTICS["London"]
    if overlaps:
        score, note = 4, SESSION_CHARACTERISTICS["London/New York overlap"]
    elif "New York" in active:
        score, note = 3, SESSION_CHARACTERISTICS["New York"]
    if not is_market_open(when):
        score, note = 0, "Market closed (weekend)."
    return {
        "utc": when,
        "sessions": active,
        "overlaps": overlaps,
        "liquidity_score": score,
        "note": note,
    }
