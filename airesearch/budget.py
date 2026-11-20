"""Hard budget. The author sets caps in budget/config.json; spending beyond a cap is refused.

The author decides money (author-notes.md). Agents may only record spend, never raise caps.
"""
import csv
import time
from pathlib import Path

from .util import now_iso, read_json


class BudgetError(Exception):
    pass


def _paths(root: Path):
    return Path(root) / "budget" / "config.json", Path(root) / "budget" / "ledger.csv"


def _read_ledger(ledger: Path) -> list:
    if not ledger.exists():
        return []
    with open(ledger, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def month_total(rows: list, month: str) -> float:
    return sum(float(r["amount_eur"]) for r in rows if r["time"].startswith(month))


def run_total(rows: list, run: str) -> float:
    return sum(float(r["amount_eur"]) for r in rows if r["run"] == run)


def spend(root: Path, run: str, amount_eur: float, note: str, when: str | None = None) -> dict:
    cfg_path, ledger = _paths(root)
    if not cfg_path.exists():
        raise BudgetError("budget/config.json missing; the author must set caps first")
    if amount_eur < 0:
        raise BudgetError("amount must be >= 0")
    cfg = read_json(cfg_path)
    when = when or now_iso()
    rows = _read_ledger(ledger)
    month = when[:7]
    if month_total(rows, month) + amount_eur > cfg["monthly_cap_eur"]:
        raise BudgetError(f"monthly cap {cfg['monthly_cap_eur']} EUR would be exceeded; ask the author")
    if run_total(rows, run) + amount_eur > cfg["per_run_cap_eur"]:
        raise BudgetError(f"per-run cap {cfg['per_run_cap_eur']} EUR would be exceeded; ask the author")
    ledger.parent.mkdir(parents=True, exist_ok=True)
    new = not ledger.exists()
    with open(ledger, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["time", "run", "amount_eur", "note"])
        w.writerow([when, run, f"{amount_eur:.2f}", note])
    return {"month_total": month_total(_read_ledger(ledger), month), "monthly_cap": cfg["monthly_cap_eur"]}


def status(root: Path) -> dict:
    cfg_path, ledger = _paths(root)
    cfg = read_json(cfg_path) if cfg_path.exists() else None
    rows = _read_ledger(ledger)
    month = time.strftime("%Y-%m", time.gmtime())
    return {"config": cfg, "month": month, "month_total_eur": month_total(rows, month), "entries": len(rows)}
