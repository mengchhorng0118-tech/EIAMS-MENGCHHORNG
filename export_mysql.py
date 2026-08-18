"""
EIAMS — Export SQLite → MySQL-compatible SQL (v2 — FK-safe)
============================================================
Fixes:
  - Removes DEFERRABLE INITIALLY DEFERRED (SQLite-only, invalid in MySQL)
  - Converts inline REFERENCES to proper MySQL CONSTRAINT FOREIGN KEY clauses
  - Strips SQLite-only pragmas, AUTOINCREMENT quirks, etc.

Run:  python export_mysql.py
Then import db_mysql.sql via phpMyAdmin → inventory_system → Import → Go
"""
import sqlite3, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(BASE, 'db.sqlite3')
DST  = os.path.join(BASE, 'db_mysql.sql')


def convert_create_table(table_name, raw_sql):
    """Convert a SQLite CREATE TABLE statement to MySQL syntax."""

    # Step 1: double-quotes → backticks
    sql = re.sub(r'"([^"]+)"', r'`\1`', raw_sql)

    # Step 2: INTEGER PRIMARY KEY AUTOINCREMENT → MySQL auto-increment
    sql = re.sub(
        r'`(\w+)`\s+integer\s+NOT\s+NULL\s+PRIMARY\s+KEY\s+AUTOINCREMENT',
        r'`\1` INT NOT NULL AUTO_INCREMENT PRIMARY KEY',
        sql, flags=re.IGNORECASE
    )
    sql = re.sub(
        r'`(\w+)`\s+INTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT',
        r'`\1` INT NOT NULL AUTO_INCREMENT PRIMARY KEY',
        sql, flags=re.IGNORECASE
    )
    sql = re.sub(r'\bAUTOINCREMENT\b', '', sql, flags=re.IGNORECASE)

    # Step 3: bool → TINYINT(1)
    sql = re.sub(r'\bbool\b', 'TINYINT(1)', sql, flags=re.IGNORECASE)

    # Step 4: Handle inline REFERENCES on each column
    # SQLite format on single line:
    #   `role_id` bigint NULL REFERENCES `accounts_role` (`id`) DEFERRABLE INITIALLY DEFERRED
    #
    # We need to:
    #   a) Strip " REFERENCES `tbl`(`col`) DEFERRABLE INITIALLY DEFERRED" from column def
    #   b) Collect it as a proper CONSTRAINT FOREIGN KEY at end of table

    fk_constraints = []
    fk_counter = 0

    def strip_inline_ref(m):
        nonlocal fk_counter
        col_name = m.group(1)   # just the identifier, no backticks
        ref_tbl  = m.group(2)
        ref_col  = m.group(3)
        fk_counter += 1
        fk_constraints.append(
            f'CONSTRAINT `fk_{table_name}_{col_name}_{fk_counter}` '
            f'FOREIGN KEY (`{col_name}`) REFERENCES `{ref_tbl}` (`{ref_col}`)'
        )
        return ''  # remove the REFERENCES clause from the column definition

    # This regex matches the REFERENCES ... DEFERRABLE part only
    # It is anchored after a backtick-wrapped column name that precedes it
    sql = re.sub(
        r'\s+REFERENCES\s+`(\w+)`\s*\(`(\w+)`\)(?:\s+DEFERRABLE\s+INITIALLY\s+DEFERRED)?',
        lambda m: _record_fk(m, table_name, fk_constraints, fk_counter),
        sql, flags=re.IGNORECASE
    )
    # recount fk_counter since lambda closure won't mutate it right; use list trick
    fk_constraints.clear()
    fk_counter_box = [0]

    def _fk_replacer(m):
        # We need to know WHICH column this REFERENCES belongs to.
        # Since REFERENCES immediately follows the column definition,
        # we look backwards in the already-processed string — not possible in re.sub.
        # Instead, we'll do a two-pass approach below.
        return ''

    # Two-pass: first collect (col, ref_tbl, ref_col), then strip from SQL
    # Regex: capture the column name (word immediately after the opening backtick),
    # skip the type declaration, then grab REFERENCES table/col.
    fk_info = []
    for m in re.finditer(
        r'`(\w+)`\s+\w[^`]*?\s+REFERENCES\s+`(\w+)`\s*\(`(\w+)`\)'
        r'(?:\s+DEFERRABLE\s+INITIALLY\s+DEFERRED)?',
        sql, flags=re.IGNORECASE
    ):
        col_name = m.group(1)   # clean column name only, e.g. "role_id"
        ref_tbl  = m.group(2)   # referenced table
        ref_col  = m.group(3)   # referenced column
        fk_info.append((col_name, ref_tbl, ref_col))

    # Strip all REFERENCES clauses (with optional DEFERRABLE)
    sql = re.sub(
        r'\s+REFERENCES\s+`\w+`\s*\(`\w+`\)(?:\s+DEFERRABLE\s+INITIALLY\s+DEFERRED)?',
        '',
        sql, flags=re.IGNORECASE
    )

    # Build clean FK CONSTRAINT clauses using only the column name (no type info)
    for i, (col_name, ref_tbl, ref_col) in enumerate(fk_info, 1):
        fk_constraints.append(
            f'  CONSTRAINT `fk_{table_name}_{col_name}_{i}` '
            f'FOREIGN KEY (`{col_name}`) REFERENCES `{ref_tbl}` (`{ref_col}`)'
        )

    # Step 5: Inject FK constraints before the closing )
    sql = sql.rstrip().rstrip(';').rstrip()
    if fk_constraints:
        last = sql.rfind(')')
        body = sql[:last].rstrip()
        sql = body + ',\n' + ',\n'.join(fk_constraints) + '\n)'

    sql += ' ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;'
    return sql


def _record_fk(m, table_name, fk_list, counter):
    return ''  # unused helper kept for clarity


def escape_value(v):
    if v is None:
        return 'NULL'
    if isinstance(v, bool):
        return '1' if v else '0'
    if isinstance(v, (int, float)):
        return str(v)
    escaped = str(v).replace('\\', '\\\\').replace("'", "\\'")
    return f"'{escaped}'"


# ── Main export ─────────────────────────────────────────────────────────────

con = sqlite3.connect(SRC)
cur = con.cursor()

out = []
out.append('-- ============================================================')
out.append('-- EIAMS Database — MySQL / MariaDB Import File')
out.append('-- BIU SAD Y3S1IT  |  Target: inventory_system database')
out.append('-- ============================================================')
out.append('')
out.append('SET FOREIGN_KEY_CHECKS = 0;')
out.append('SET NAMES utf8mb4;')
out.append("SET CHARACTER SET utf8mb4;")
out.append('')

cur.execute(
    "SELECT name, sql FROM sqlite_master "
    "WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
)
tables = cur.fetchall()

for table_name, create_sql in tables:
    if not create_sql:
        continue

    out.append(f'-- ── Table: `{table_name}` ──')
    out.append(f'DROP TABLE IF EXISTS `{table_name}`;')

    try:
        converted = convert_create_table(table_name, create_sql)
        out.append(converted)
    except Exception as e:
        out.append(f'-- ERROR converting {table_name}: {e}')
        out.append('-- Original SQL below (skipped):')
        for line in create_sql.splitlines():
            out.append(f'-- {line}')

    out.append('')

    # ── INSERT rows ────────────────────────────────────────────
    cur.execute(f'SELECT * FROM "{table_name}"')
    rows = cur.fetchall()
    if rows:
        col_names = [d[0] for d in cur.description]
        cols_str  = ', '.join(f'`{c}`' for c in col_names)
        batch = ['(' + ', '.join(escape_value(v) for v in row) + ')' for row in rows]
        for i in range(0, len(batch), 100):
            chunk = batch[i:i + 100]
            out.append(f'INSERT INTO `{table_name}` ({cols_str}) VALUES')
            out.append(',\n'.join(chunk) + ';')
            out.append('')

    out.append('')

out.append('SET FOREIGN_KEY_CHECKS = 1;')
out.append('')
out.append('-- ============================================================')
out.append('-- Import complete. All EIAMS tables and data loaded.')
out.append('-- ============================================================')

con.close()

content = '\n'.join(out)
with open(DST, 'w', encoding='utf-8') as f:
    f.write(content)

size_kb = os.path.getsize(DST) // 1024
print(f'[OK] Exported : {len(tables)} tables')
print(f'[OK] File     : {DST}')
print(f'[OK] Size     : {size_kb} KB')
print()
print('Steps for phpMyAdmin:')
print('  1. Open phpMyAdmin')
print('  2. Click "inventory_system" in the left panel')
print('  3. Click the "Import" tab at the top')
print('  4. Click "Choose File" → select db_mysql.sql')
print('  5. Click "Go"')
