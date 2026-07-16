#!/usr/bin/env python3
"""
build_db.py - build a normalized SQLite database from the committed CSVs.

The flat CSVs in 02-data/ are the source of record. This turns them into a real relational
database a reader can query: meetings, board members, the 72 questioned resolutions, and a
normalized junction table of who asked what, plus the peer boards. It rebuilds deterministically
and asserts the headline figures with SQL before it writes anything.

    python 03-harness/build_db.py            # (re)build db/pittsburgh_water.db and db/schema.sql
    python 03-harness/build_db.py --check    # rebuild to a temp file, assert, write nothing

Query it:
    sqlite3 db/pittsburgh_water.db "SELECT * FROM v_headline;"
"""
import argparse, csv, pathlib, sqlite3, sys, tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ap = argparse.ArgumentParser()
ap.add_argument("--check", action="store_true", help="build to a temp file and assert; write nothing")
ARGS = ap.parse_args()

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "02-data"
DBDIR = ROOT / "db"
DBDIR.mkdir(exist_ok=True)
DBPATH = (pathlib.Path(tempfile.mkdtemp()) / "check.db") if ARGS.check else (DBDIR / "pittsburgh_water.db")

MEMBER_NAMES = {
    "sciulli": "Alex Sciulli", "domach": "Michael Domach", "leber": "BJ Leber",
    "strassburger": "Erika Strassburger", "martin": "James Martin",
    "mccormick_barron": "Peg McCormick Barron", "murrell": "Audrey Murrell", "bey": "Jamil Bey",
}


def read(name):
    with open(DATA / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(v):
    v = (v or "").strip()
    return None if v == "" or v.upper() == "NA" else (float(v) if "." in v else int(v))


SCHEMA = """
PRAGMA foreign_keys = ON;

-- One row per board meeting (the census spine).
CREATE TABLE meetings (
  meeting_no        INTEGER PRIMARY KEY,
  meeting_date      TEXT NOT NULL,
  total_resolutions INTEGER NOT NULL,
  unanimous         INTEGER NOT NULL,
  abstentions       INTEGER NOT NULL,
  split_votes       INTEGER NOT NULL,
  questions_asked   INTEGER NOT NULL,   -- counted per meeting (sums to 131)
  dollars_millions  REAL    NOT NULL,
  public_speakers   INTEGER NOT NULL,
  notable_items     TEXT
);

CREATE TABLE board_members (
  member_id             TEXT PRIMARY KEY,   -- e.g. 'sciulli'
  name                  TEXT NOT NULL,
  role                  TEXT,
  meetings_active       INTEGER,
  questions_by_meeting  INTEGER,            -- per-meeting count (sums to 131)
  questions_by_resolution INTEGER          -- resolution-attributed count (sums to 96)
);

-- The 72 resolutions that drew at least one recorded question.
CREATE TABLE questioned_resolutions (
  resolution_no   TEXT PRIMARY KEY,        -- e.g. 'No. 74 of 2024'
  year            INTEGER NOT NULL,
  total_questions INTEGER NOT NULL
);

-- Normalized junction: who asked how many questions on which resolution (non-zero cells only).
CREATE TABLE resolution_questions (
  resolution_no  TEXT NOT NULL REFERENCES questioned_resolutions(resolution_no),
  member_id      TEXT NOT NULL REFERENCES board_members(member_id),
  question_count INTEGER NOT NULL CHECK (question_count > 0),
  PRIMARY KEY (resolution_no, member_id)
);
CREATE INDEX idx_rq_member ON resolution_questions(member_id);

CREATE TABLE peer_boards (
  utility          TEXT PRIMARY KEY,
  jurisdiction     TEXT,
  meetings_sampled INTEGER,
  sampling_method  TEXT,
  votes            INTEGER,
  unanimous        INTEGER,
  contested        INTEGER,
  abstentions      INTEGER,
  unanimity_pct    REAL,
  longest_meeting_min INTEGER,
  exemplar         TEXT
);

-- Headline figures, computed in SQL so a reader can see the arithmetic.
CREATE VIEW v_headline AS
SELECT
  (SELECT COUNT(*)                 FROM meetings)                     AS meetings,
  (SELECT SUM(total_resolutions)   FROM meetings)                     AS resolutions,
  (SELECT SUM(unanimous)           FROM meetings)                     AS unanimous,
  (SELECT SUM(split_votes)         FROM meetings)                     AS split_votes,
  (SELECT SUM(abstentions)         FROM meetings)                     AS abstentions,
  (SELECT ROUND(SUM(dollars_millions),2) FROM meetings)              AS dollars_millions,
  (SELECT SUM(public_speakers)     FROM meetings)                     AS public_speakers,
  (SELECT COUNT(*)                 FROM questioned_resolutions)       AS resolutions_questioned,
  (SELECT SUM(total_resolutions)   FROM meetings)
    - (SELECT COUNT(*)             FROM questioned_resolutions)       AS resolutions_unquestioned,
  (SELECT SUM(question_count)      FROM resolution_questions)         AS questions_attributed;

-- Recompute each member's resolution-attributed total from the junction table.
CREATE VIEW v_questions_by_member AS
SELECT bm.name, bm.role,
       COALESCE(SUM(rq.question_count), 0) AS questions_by_resolution
FROM board_members bm
LEFT JOIN resolution_questions rq ON rq.member_id = bm.member_id
GROUP BY bm.member_id
ORDER BY questions_by_resolution DESC;
"""


def build(conn):
    conn.executescript(SCHEMA)
    c = conn.cursor()

    for r in read("meetings.csv"):
        c.execute("""INSERT INTO meetings VALUES (?,?,?,?,?,?,?,?,?,?)""",
                  (num(r["meeting_no"]), r["meeting_date"], num(r["total_resolutions"]),
                   num(r["unanimous"]), num(r["abstentions"]), num(r["split_votes"]),
                   num(r["questions_asked"]), num(r["dollars_millions"]),
                   num(r["public_speakers"]), r["notable_items"]))

    for r in read("questions_by_member.csv"):
        mid = next(k for k, v in MEMBER_NAMES.items() if v == r["member"])
        c.execute("""INSERT INTO board_members VALUES (?,?,?,?,?,?)""",
                  (mid, r["member"], r["role"], num(r["meetings_active"]),
                   num(r["questions_by_meeting"]), num(r["questions_by_resolution"])))

    for r in read("questions_by_resolution.csv"):
        c.execute("INSERT INTO questioned_resolutions VALUES (?,?,?)",
                  (r["resolution"], num(r["year"]), num(r["total"])))
        for mid in MEMBER_NAMES:
            n = num(r[mid])
            if n:
                c.execute("INSERT INTO resolution_questions VALUES (?,?,?)", (r["resolution"], mid, n))

    for r in read("peer_comparison.csv"):
        c.execute("""INSERT INTO peer_boards VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                  (r["utility"], r["jurisdiction"], num(r["meetings_sampled"]), r["sampling_method"],
                   num(r["votes"]), num(r["unanimous"]), num(r["contested"]), num(r["abstentions"]),
                   num(r["unanimity_pct"]), num(r["longest_meeting_min"]), r["exemplar"]))
    conn.commit()


def assert_figures(conn):
    h = dict(zip([d[0] for d in conn.execute("SELECT * FROM v_headline").description],
                 conn.execute("SELECT * FROM v_headline").fetchone()))
    expect = {"meetings": 24, "resolutions": 228, "unanimous": 223, "split_votes": 0,
              "abstentions": 5, "public_speakers": 10, "resolutions_questioned": 72,
              "resolutions_unquestioned": 156, "questions_attributed": 96}
    bad = [f"{k}: got {h[k]}, expected {v}" for k, v in expect.items() if h[k] != v]
    if abs(h["dollars_millions"] - 871.25) > 0.01:
        bad.append(f"dollars_millions: got {h['dollars_millions']}, expected 871.25")
    return h, bad


conn = sqlite3.connect(DBPATH)
build(conn)
h, bad = assert_figures(conn)
print("Headline figures from SQL (SELECT * FROM v_headline):")
for k, v in h.items():
    print(f"  {k}: {v}")
if bad:
    print("\nASSERTION FAILED:")
    for b in bad:
        print("  -", b)
    conn.close()
    sys.exit(1)

if not ARGS.check:
    (DBDIR / "schema.sql").write_text(SCHEMA.strip() + "\n", encoding="utf-8")
    rows = conn.execute("SELECT COUNT(*) FROM resolution_questions").fetchone()[0]
    print(f"\nwrote {DBPATH.relative_to(ROOT)} and db/schema.sql")
    print(f"normalized {rows} member-resolution question rows from the 72-resolution pivot")
else:
    print("\nfigures reproduce from the rebuilt database; nothing written.")
conn.close()
