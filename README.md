# Tallyturnstone

Manual named counters with logged signed adjustments, confirmed undo and CSV export. Generic hobby/session bookkeeping, not payment accounting, secure inventory, medical tracking or an authoritative audit ledger. No automatic sensing or external tracking.

Python 3.9+, standard library only. Published in a private GitHub repository. Download its ZIP while signed into the owner account, extract it and open a terminal inside the source folder. Not verified as store-installed.

```text
python3 tallyturnstone.py
python3 tallyturnstone.py --db demo.sqlite3
python3 -m unittest -v
bash app-store.sh install
bash app-store.sh run
```

Counters start at zero. Names are unique and case-sensitive. Adjustments are nonzero signed integers; resulting count must stay 0..1e9. Enter a delta, not a target total. For example +5 adds five, -2 removes two. Counter name/current count is shown before adjustment. Invalid/out-of-range changes are rejected without a history entry.

Undo confirms and reverses the latest not-yet-undone adjustment for that counter, preserving its row as undone. It can continue back through older active adjustments. A new adjustment doesn't erase earlier undo records. No redo, deletion, reset or rename. One app instance per database is recommended; SQLite stores changes atomically but this isn't a multi-user synchronization service.

Default database: `~/.local/share/tallyturnstone/counts.sqlite3`, outside code folder. Completed changes commit immediately. Permissions set owner-only where supported, not encrypted. Local database can be edited externally, so history is not tamper-proof. Back up the closed database file yourself. Recent history shows up to 30 rows per counter.

CSV reports include ID/name/current count, not full adjustment history. Formula-like names get an apostrophe prefix for spreadsheet reading. Reports refuse overwrite. No import, network, accounts, spending or automatic commitments. Root marker/version published.

17 tests cover bounds, rollback, signed adjustments, LIFO/independent undo, duplicate names, SQL-shaped text as data, persistence, CSV protection and CLI. Linux tested; Pi/non-Linux untested.

The current public-only Pi App Store cannot discover private repositories; authenticated store support is not verified.
