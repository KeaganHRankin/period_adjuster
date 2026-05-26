"""
keaganhrankin 2026
Period Adjuster
"""
import argparse
from pathlib import Path
import sqlite3
import yaml


def adjust_periods(path: str, tables: list, x: int, forwards=True):
    """
    Given tables in a SQLite database, updates each table's
    `period` column by `x` years forward or backward.

    Rows are updated in a safe order so unique constraints that include
    `period` do not collide while the values are being shifted.
    """
    step = abs(x)
    shift = step if forwards else -step
    order = "DESC" if forwards else "ASC"

    conn = sqlite3.connect(path)
    cur = conn.cursor()
    updated_rows = {}

    try:
        for table in tables:
            cur.execute(
                f'SELECT rowid FROM "{table}" ORDER BY period {order}'
            )
            rowids = [row[0] for row in cur.fetchall()]

            updated_count = 0
            for rowid in rowids:
                cur.execute(
                    f'UPDATE "{table}" SET period = period + ? WHERE rowid = ?',
                    (shift, rowid),
                )
                updated_count += cur.rowcount if cur.rowcount is not None else 0

            updated_rows[table] = updated_count

        conn.commit()
    finally:
        conn.close()

    direction = 'forward' if forwards else 'backward'
    print(f"adjust_periods: shifted {len(updated_rows)} table(s) {direction} by {step} year(s).")
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


def adjust_all_periods(path: str, x: int, forwards=True):
    """Find all tables with a `period` column and shift them by `x` years."""
    tables = get_tables_with_period(path)
    return adjust_periods(path, tables, x, forwards=forwards)


def adjust_selected_periods(path: str, tables: list, x: int, forwards=True):
    """Shift only the selected tables, or all tables when the list is empty."""
    if not tables:
        tables = get_tables_with_period(path)
    return adjust_periods(path, tables, x, forwards=forwards)


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
        default=str(script_dir / "adjust_periods.yml"),
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
    tables = config.get("tables", []) or []

    updated = adjust_selected_periods(db_path, tables, x, forwards=forwards)
    print(updated)