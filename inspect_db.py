"""
inspect_db.py
=============
Standalone script to connect to the project's SQLite database and
display all tables, row counts, and sample data.

Usage:
    python inspect_db.py                  # show all tables + row counts
    python inspect_db.py accounts_user    # show first 10 rows of a table
    python inspect_db.py --all            # dump every table's data
"""

import sqlite3
import sys
import os

# ── Path to the database ──────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "db.sqlite3")


def connect() -> sqlite3.Connection:
    """Open a read-only connection to the SQLite file."""
    if not os.path.exists(DB_PATH):
        print(f"❌  Database not found: {DB_PATH}")
        print("   Run:  python manage.py migrate")
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # access columns by name
    return conn


def list_tables(conn: sqlite3.Connection) -> list[str]:
    """Return all user-created table names sorted alphabetically."""
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    return [row[0] for row in cur.fetchall()]


def row_count(conn: sqlite3.Connection, table: str) -> int:
    cur = conn.execute(f'SELECT COUNT(*) FROM "{table}"')
    return cur.fetchone()[0]


def show_table(conn: sqlite3.Connection, table: str, limit: int = 10) -> None:
    """Print column names and up to `limit` rows for a given table."""
    print(f"\n{'═' * 70}")
    print(f"  TABLE: {table}")
    print(f"{'═' * 70}")
    try:
        cur = conn.execute(f'SELECT * FROM "{table}" LIMIT {limit}')
        rows = cur.fetchall()
        if not rows:
            print("  (empty table)")
            return
        # Header
        cols = [desc[0] for desc in cur.description]
        col_widths = [max(len(c), 12) for c in cols]
        header = "  " + " | ".join(c.ljust(w) for c, w in zip(cols, col_widths))
        print(header)
        print("  " + "-" * (len(header) - 2))
        # Rows
        for row in rows:
            line = "  " + " | ".join(
                str(row[c])[:w].ljust(w) for c, w in zip(cols, col_widths)
            )
            print(line)
        total = row_count(conn, table)
        if total > limit:
            print(f"\n  ... and {total - limit} more rows (total: {total})")
        else:
            print(f"\n  Total rows: {total}")
    except sqlite3.OperationalError as e:
        print(f"  ⚠  {e}")


def main() -> None:
    conn   = connect()
    tables = list_tables(conn)

    args = sys.argv[1:]

    # ── No args: show summary of all tables ──────────────────────
    if not args:
        print(f"\n{'═' * 70}")
        print(f"  DATABASE: {DB_PATH}")
        print(f"{'═' * 70}")
        print(f"  {'Table':<45} {'Rows':>8}")
        print(f"  {'-'*45} {'-'*8}")
        for t in tables:
            count = row_count(conn, t)
            print(f"  {t:<45} {count:>8}")
        print(f"\n  Total tables: {len(tables)}")
        print("\n  Tip: python inspect_db.py <table_name>   — view table data")
        print("       python inspect_db.py --all          — dump all tables")
        conn.close()
        return

    # ── --all: dump every table ───────────────────────────────────
    if "--all" in args:
        for t in tables:
            show_table(conn, t)
        conn.close()
        return

    # ── Specific table name ───────────────────────────────────────
    table_name = args[0]
    if table_name not in tables:
        # Case-insensitive search
        matches = [t for t in tables if t.lower() == table_name.lower()]
        if matches:
            table_name = matches[0]
        else:
            print(f"\n❌  Table '{table_name}' not found.")
            print(f"\nAvailable tables:\n  " + "\n  ".join(tables))
            conn.close()
            sys.exit(1)

    limit = 20
    if len(args) > 1 and args[1].isdigit():
        limit = int(args[1])

    show_table(conn, table_name, limit)
    conn.close()


if __name__ == "__main__":
    main()
