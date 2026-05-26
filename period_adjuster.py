"""
keaganhrankin 2026
Period Adjuster
"""
import argparse
from pathlib import Path
import sqlite3
import yaml


def period_adjuster(path: str, tables: list, x: int, forwards=True):
    """
    Given tables in a SQLite database, updates each table's
    `period` column by `x` years forward or backward.
    """
    step = abs(x)
    shift = step if forwards else -step

    conn = sqlite3.connect(path)
    cur = conn.cursor()
    updated_rows = {}

    for table in tables:
        cur.execute(f'UPDATE "{table}" SET period = period + ?', (shift,))
        updated_rows[table] = cur.rowcount if cur.rowcount is not None else 0

    conn.commit()
    conn.close()

    direction = 'forward' if forwards else 'backward'
    print(f"period_adjuster: shifted {len(updated_rows)} table(s) {direction} by {step} year(s).")
    return updated_rows


def get_tables_with_period(path: str):
    """Return a list of SQLite tables that contain a `period` column."""
    conn = sqlite3.connect(path)
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    table_names = [row[0] for row in cur.fetchall()]

    tables_with_period = []
    for table in table_names:
        cur.execute(f'PRAGMA table_info("{table}")')
        columns = [row[1] for row in cur.fetchall()]
        if 'period' in columns:
            tables_with_period.append(table)

    conn.close()
    return tables_with_period


def period_adjuster_all(path: str, x: int, forwards=True):
    """Find all tables with a `period` column and shift them by `x` years."""
    tables = get_tables_with_period(path)
    return period_adjuster(path, tables, x, forwards=forwards)


def _load_config(config_path: str):
    with open(config_path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(
        description="Shift the period column in every SQLite table that has one."
    )
    parser.add_argument(
        "config",
        nargs="?",
        default=str(script_dir / "period_adjuster.yml"),
        help="Path to a YAML config file in the same directory as this script.",
    )
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = script_dir / config_path

    config = _load_config(config_path)
    db_path = config["path"]
    x = config["x"]
    forwards = config.get("forwards", True)

    updated = period_adjuster_all(db_path, x, forwards=forwards)
    print(updated)