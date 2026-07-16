# The database

A normalized SQLite database of the coded Pittsburgh Water board record. The flat CSVs in
`../02-data/` are the source of record; this is those records as a relational database you can
query. It is rebuilt deterministically by `../03-harness/build_db.py`, which asserts every headline
figure in SQL before it writes the file.

## Three ways to query it

- **In the browser, no install:** open [`index.html`](index.html) (live at
  `/db/index.html`). It loads the database with sql.js and runs SQL right on the page, with the
  example queries one click away.
- **Command line:** `sqlite3 db/pittsburgh_water.db "SELECT * FROM v_headline;"`
- **A GUI:** open `pittsburgh_water.db` in [DB Browser for SQLite](https://sqlitebrowser.org/).

Example queries live in [`queries.sql`](queries.sql). The full schema is in
[`schema.sql`](schema.sql).

## The schema

| Table | One row per | Key columns |
|---|---|---|
| `meetings` | board meeting (24) | date, resolutions, unanimous, abstentions, split_votes, questions, dollars_millions, public_speakers |
| `board_members` | member (8) | name, role, questions_by_meeting (131 total), questions_by_resolution (96 total) |
| `questioned_resolutions` | resolution that drew a question (72) | resolution_no, year, total_questions |
| `resolution_questions` | member-resolution question (82) | resolution_no → member_id, question_count |
| `peer_boards` | utility in the peer test | votes, unanimous, contested, unanimity_pct |

`resolution_questions` is the normalization that the CSV could not show cleanly: the wide
"resolution × member" pivot turned into one row per member per resolution, so `SUM(question_count)`
returns the 96 resolution-attributed questions and every per-member total recomputes from it.

Two views compute the findings in SQL so the arithmetic is visible, not asserted:
`v_headline` (every headline figure in one row) and `v_questions_by_member` (each member's total,
rebuilt from the junction table).

## Rebuild it

```
python 03-harness/build_db.py           # rebuild the .db and schema.sql
python 03-harness/build_db.py --check    # rebuild to a temp file, assert the figures, write nothing
```

The two question totals (131 counted per meeting, 96 attributed to specific resolutions) are
reconciled in `../FACT-CHECK.md`; both are represented here, in `board_members` and in the
junction table respectively.
