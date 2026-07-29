"""One-time script: drops old asset tables and clears migration history."""
import sqlite3, os, sys

db = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
conn = sqlite3.connect(db)
cur  = conn.cursor()

tables = [
    'assets_assettransfer', 'assets_transferhistory',
    'assets_maintenancerecord', 'assets_assetdisposal',
    'assets_assetauditlog', 'assets_asset',
]
for t in tables:
    cur.execute(f"DROP TABLE IF EXISTS [{t}]")
    print(f"Dropped {t}")

cur.execute("DELETE FROM django_migrations WHERE app='assets'")
print("Cleared assets from django_migrations")
conn.commit()
conn.close()
print("Done.")
