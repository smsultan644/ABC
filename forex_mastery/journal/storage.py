"""
Journal storage: CSV as the source of truth, JSON as the interchange format.

WHY CSV
-------
* Openable in Excel, LibreOffice, Google Sheets and pandas without a database.
* Diffs cleanly in git if you choose to version it (you probably should not
  version a live journal in a public repo).
* No lock-in: the analysis code here and any external tool can read it.

The store is deliberately small and explicit. ``write`` overwrites atomically
(write to a temporary file, then replace) so a crash mid-save cannot destroy
your journal - a real concern when a journal holds months of work.
"""

from __future__ import annotations

import csv
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable, Iterator

from .model import JOURNAL_COLUMNS, TradeRecord

__all__ = ["JournalStore", "default_journal_path"]


def default_journal_path(root: Path | None = None) -> Path:
    """``<repo>/data/journal/journal.csv`` (searched upward from this file)."""
    if root is not None:
        return Path(root) / "data" / "journal" / "journal.csv"
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "data").is_dir():
            return parent / "data" / "journal" / "journal.csv"
    return Path.cwd() / "data" / "journal" / "journal.csv"


@dataclass
class JournalStore:
    """Read/write access to a CSV trading journal.

    Examples
    --------
    >>> import tempfile, pathlib
    >>> tmp = pathlib.Path(tempfile.mkdtemp()) / "journal.csv"
    >>> store = JournalStore(tmp)
    >>> trade = TradeRecord(trade_id="T1", date="2026-09-15", symbol="EURUSD",
    ...                     direction="long", entry=1.10, stop_loss=1.0950,
    ...                     take_profit=1.11, lots=0.01, risk_amount=1.25,
    ...                     account_equity_at_entry=250.0, pnl=3.75)
    >>> _ = store.add(trade)
    >>> len(store.load())
    1
    >>> round(store.load()[0].r_multiple, 2)
    3.0
    """

    path: Path

    def __post_init__(self) -> None:
        self.path = Path(self.path)

    # ------------------------------------------------------------------ #
    def exists(self) -> bool:
        return self.path.is_file()

    def load(self, include_open: bool = True) -> list[TradeRecord]:
        """Read all records. Bad rows raise, naming the line number."""
        if not self.path.is_file():
            return []
        records: list[TradeRecord] = []
        with self.path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for line_number, row in enumerate(reader, start=2):
                if not any((v or "").strip() for v in row.values()):
                    continue  # blank line
                try:
                    record = TradeRecord.from_row(row)
                except Exception as exc:  # pragma: no cover - defensive
                    raise ValueError(f"{self.path}:{line_number}: {exc}") from exc
                if include_open or record.is_closed:
                    records.append(record)
        return records

    def iter_closed(self) -> Iterator[TradeRecord]:
        return (r for r in self.load() if r.is_closed)

    # ------------------------------------------------------------------ #
    def write(self, records: Iterable[TradeRecord]) -> Path:
        """Atomically write the whole journal."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        rows = [r.to_row() for r in records]
        fd, tmp_name = tempfile.mkstemp(dir=str(self.path.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(JOURNAL_COLUMNS))
                writer.writeheader()
                for row in rows:
                    writer.writerow(row)
            os.replace(tmp_name, self.path)
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)
        return self.path

    def add(self, record: TradeRecord) -> TradeRecord:
        """Append one trade and rewrite the file."""
        records = self.load()
        records.append(record)
        self.write(records)
        return record

    def update(self, trade_id: str, **changes: Any) -> TradeRecord:
        """Patch an existing trade by id (e.g. to close it)."""
        records = self.load()
        for index, record in enumerate(records):
            if record.trade_id == trade_id:
                for key, value in changes.items():
                    if not hasattr(record, key):
                        raise KeyError(f"Unknown field {key!r} on TradeRecord")
                    setattr(record, key, value)
                record.__post_init__()
                records[index] = record
                self.write(records)
                return record
        raise KeyError(f"No trade with id {trade_id!r}")

    def next_trade_id(self, prefix: str = "T") -> str:
        """Sequential id in the form ``T-0007``."""
        existing = self.load()
        highest = 0
        for record in existing:
            digits = "".join(ch for ch in str(record.trade_id).split("-")[-1] if ch.isdigit())
            if digits:
                highest = max(highest, int(digits))
        return f"{prefix}-{highest + 1:04d}"

    # ------------------------------------------------------------------ #
    def export_json(self, target: Path) -> Path:
        target = Path(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = [r.as_dict() for r in self.load()]
        target.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        return target

    def import_json(self, source: Path, replace: bool = False) -> list[TradeRecord]:
        payload = json.loads(Path(source).read_text(encoding="utf-8"))
        fields = set(TradeRecord.__dataclass_fields__)
        records = []
        for item in payload:
            # Keep unknown/derived keys (e.g. r_multiple) in `extra` rather than
            # passing them as constructor arguments.
            known = {k: v for k, v in item.items() if k in fields and k != "extra"}
            extra = dict(item.get("extra") or {})
            extra.update({k: v for k, v in item.items() if k not in fields})
            records.append(TradeRecord(**known, extra=extra))
        if replace:
            self.write(records)
        else:
            existing = self.load()
            self.write([*existing, *records])
        return records

    def close_trade(
        self,
        trade_id: str,
        *,
        exit_price: float,
        pnl: float,
        exit_time: str | None = None,
        reason_for_exit: str = "",
        thesis_valid: bool | None = None,
        lesson: str = "",
    ) -> TradeRecord:
        """Record the outcome of a trade, keeping risk and R consistent."""
        return self.update(
            trade_id,
            exit_price=exit_price,
            pnl=pnl,
            exit_time=exit_time or datetime.now().isoformat(timespec="minutes"),
            reason_for_exit=reason_for_exit,
            thesis_valid=thesis_valid,
            lesson=lesson,
            status="win" if pnl > 0 else ("loss" if pnl < 0 else "breakeven"),
        )

    def summary(self) -> dict[str, Any]:
        """Very small overview (full statistics live in core.metrics)."""
        records = self.load()
        closed = [r for r in records if r.is_closed]
        rs = [r.r_multiple for r in closed if r.r_multiple is not None]
        return {
            "path": str(self.path),
            "total_records": len(records),
            "closed": len(closed),
            "open": len(records) - len(closed),
            "net_pnl": sum(r.pnl or 0.0 for r in closed),
            "total_r": sum(rs) if rs else 0.0,
            "win_rate": (
                sum(1 for r in closed if (r.pnl or 0) > 0) / len(closed) * 100.0 if closed else 0.0
            ),
            "first_date": min((str(r.date) for r in records), default=None),
            "last_date": max((str(r.date) for r in records), default=None),
        }

    def ensure_template(self) -> Path:
        """Create an empty journal with headers if none exists."""
        if not self.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.write([])
        return self.path


def new_trade_id(store: JournalStore | None = None) -> str:
    """Convenience id generator (``T-0001`` style), optionally from the journal."""
    if store is not None:
        return store.next_trade_id()
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    return f"T-{stamp}"
