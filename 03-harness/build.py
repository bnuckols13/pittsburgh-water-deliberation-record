#!/usr/bin/env python3
"""
build.py - recompute every headline figure in the Pittsburgh Water investigation from
the committed data, and refuse to finish if any of them drifts from what the published
stories say.

Deterministic and offline. It reads only the CSVs in 02-data/ (which trace, through
FIGURE-TRACE.md, to the archived board minutes in 01-sources-archive/) and writes one
derived file plus a printed report. A reader can rerun it and get the same numbers that
ran in Public Source.

    python 03-harness/build.py           # recompute, write 02-data/headline_figures.csv, print the report
    python 03-harness/build.py --check   # recompute to a temp dir and diff; write nothing

The published figures this asserts (baseline story + observer-effect follow-up):
    228 resolutions, 223 unanimous, 0 split, 5 abstentions, >$870M authorized,
    72 of 228 drew a question, 156 drew none, 10 public speakers across 5 meetings,
    peer unanimity 20/29 = 69% against Pittsburgh Water's 100%,
    40 questions at the first post-publication meeting, about 7x the 24-month average.
"""
import argparse, csv, pathlib, sys, tempfile

try:  # UTF-8 stdout so a Windows console never renders output as replacement glyphs
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ap = argparse.ArgumentParser()
ap.add_argument("--check", action="store_true",
                help="recompute to a temp dir and diff against the committed file; write nothing")
ARGS = ap.parse_args()

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "02-data"
OUT = pathlib.Path(tempfile.mkdtemp(prefix="pwdr-build-check-")) if ARGS.check else DATA

FAILS = []


def expect(name, got, want, tol=0):
    ok = abs(got - want) <= tol if isinstance(want, (int, float)) else got == want
    print(f"  [{'OK' if ok else 'DRIFT'}] {name}: {got}" + ("" if ok else f"  (expected {want})"))
    if not ok:
        FAILS.append(name)


def read(name):
    with open(DATA / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(v):
    return None if v.strip().upper() == "NA" else float(v)


# --- the census spine: meetings.csv ------------------------------------------------
meetings = read("meetings.csv")
resolutions = sum(int(r["total_resolutions"]) for r in meetings)
unanimous = sum(int(r["unanimous"]) for r in meetings)
split = sum(int(r["split_votes"]) for r in meetings)
abstentions = sum(int(r["abstentions"]) for r in meetings)
q_by_meeting = sum(int(r["questions_asked"]) for r in meetings)
speakers = sum(int(r["public_speakers"]) for r in meetings)
mtgs_with_speakers = sum(1 for r in meetings if int(r["public_speakers"]) > 0)
dollars = sum(float(r["dollars_millions"]) for r in meetings)

print("Meeting census (from meetings.csv):")
expect("meetings analyzed", len(meetings), 24)
expect("resolutions voted", resolutions, 228)
expect("unanimous votes", unanimous, 223)
expect("split votes", split, 0)
expect("abstentions", abstentions, 5)
expect("questions counted per meeting", q_by_meeting, 131)
expect("public speakers", speakers, 10)
expect("meetings with any public speaker", mtgs_with_speakers, 5)
expect("dollars authorized (millions, +/- 0.5)", round(dollars, 2), 871.25, tol=0.5)

# --- resolution-level question coding: questions_by_resolution.csv ------------------
qbr = read("questions_by_resolution.csv")
questioned = len(qbr)
q_by_resolution = sum(int(r["total"]) for r in qbr)
unquestioned = resolutions - questioned

print("\nResolution-level question coding (from questions_by_resolution.csv):")
expect("resolutions that drew a question", questioned, 72)
expect("resolutions that drew none (228 - 72)", unquestioned, 156)
expect("questions attributed to a resolution", q_by_resolution, 96)

# --- the two question totals must reconcile to their two definitions ---------------
qbm = read("questions_by_member.csv")
m_by_meeting = sum(int(r["questions_by_meeting"]) for r in qbm)
m_by_resolution = sum(int(r["questions_by_resolution"]) for r in qbm)
print("\nQuestion totals reconcile to their definitions (from questions_by_member.csv):")
expect("per-meeting total (matches meetings.csv 131)", m_by_meeting, q_by_meeting)
expect("per-resolution total (matches the pivot 96)", m_by_resolution, q_by_resolution)

# --- peer comparison: peer_comparison.csv ------------------------------------------
peers = {r["utility"]: r for r in read("peer_comparison.csv")}
pgh = peers["Pittsburgh Water"]
comb = peers["Peers combined"]


def unanimity_rate(row):
    # Rate among votes where every member participated: abstentions (recusals) leave the
    # denominator. For Pittsburgh Water that is 223 / (228 - 5) = 100%; for the peers the
    # published figure counts all 29 votes (abstentions column 0), giving 20 / 29 = 69%.
    return round(num(row["unanimous"]) / (num(row["votes"]) - num(row["abstentions"])) * 100, 1)


pgh_rate = unanimity_rate(pgh)
peer_rate = unanimity_rate(comb)
print("\nPeer comparison (from peer_comparison.csv):")
expect("Pittsburgh Water unanimity rate (223/223 when all voted)", pgh_rate, 100.0)
expect("peer unanimity rate (20/29)", peer_rate, 69.0)

# --- observer effect: follow_up.csv ------------------------------------------------
fu = {r["metric"]: r["value"] for r in read("follow_up.csv")}
follow_q = int(fu["first_post_publication_questions"])
avg_per_meeting = q_by_meeting / len(meetings)
ratio = follow_q / avg_per_meeting
print("\nObserver effect (from follow_up.csv + the census average):")
expect("questions at first post-publication meeting", follow_q, 40)
expect("24-month average questions per meeting (131/24)", round(avg_per_meeting, 2), 5.46, tol=0.01)
expect("ratio to average (about 7x)", round(ratio, 1), 7.3, tol=0.3)

# --- write the derived summary -----------------------------------------------------
out = OUT / "headline_figures.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["figure", "value", "source_file"])
    rows = [
        ("meetings_analyzed", len(meetings), "meetings.csv"),
        ("resolutions_voted", resolutions, "meetings.csv"),
        ("unanimous_votes", unanimous, "meetings.csv"),
        ("split_votes", split, "meetings.csv"),
        ("abstentions", abstentions, "meetings.csv"),
        ("dollars_authorized_millions", round(dollars, 2), "meetings.csv"),
        ("public_speakers", speakers, "meetings.csv"),
        ("meetings_with_speakers", mtgs_with_speakers, "meetings.csv"),
        ("resolutions_questioned", questioned, "questions_by_resolution.csv"),
        ("resolutions_unquestioned", unquestioned, "derived: 228 - 72"),
        ("questions_by_meeting", q_by_meeting, "meetings.csv"),
        ("questions_by_resolution", q_by_resolution, "questions_by_resolution.csv"),
        ("pgh_unanimity_pct", pgh_rate, "peer_comparison.csv"),
        ("peer_unanimity_pct", peer_rate, "peer_comparison.csv"),
        ("follow_up_questions", follow_q, "follow_up.csv"),
        ("follow_up_ratio_to_avg", round(ratio, 1), "derived: 40 / (131/24)"),
    ]
    w.writerows(rows)

if FAILS:
    print(f"\nREPRODUCTION FAILED: {len(FAILS)} figure(s) drifted from the published record:")
    for x in FAILS:
        print("  -", x)
    if ARGS.check:
        import shutil
        shutil.rmtree(OUT, ignore_errors=True)
    sys.exit(1)

if ARGS.check:
    committed = DATA / out.name
    same = committed.exists() and committed.read_bytes() == out.read_bytes()
    import shutil
    shutil.rmtree(OUT, ignore_errors=True)
    if not same:
        print("\nREPRODUCTION FAILED: headline_figures.csv rebuilt differently than committed.")
        sys.exit(1)
    print("\nreproduced every headline figure; all match the published stories.")
    sys.exit(0)

print(f"\nwrote {out.name}; every headline figure matches the published stories.")
