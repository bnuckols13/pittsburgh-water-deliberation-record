#!/usr/bin/env python3
"""
gate.py - the publication gate.

The reader contract says the gate refuses to ship while any step is incomplete. This is
that gate, in code, so it cannot be waved through at 1am.

Checks, in order:
  1. Every source in sources.json is captured and hashes clean (verify.py).
  2. Every source has a Wayback URL in PROVENANCE.md.
  3. Every headline figure reproduces from the committed data (build.py --check).
  4. The derived data is newer than the sources it draws from.
  5. CORRECTIONS.md exists (an empty ledger is fine; a missing one is not).

    python 03-harness/gate.py

Exit 0 = clear to publish. Exit 1 = not clear, with the reason. There is no --force.
"""
import json, pathlib, re, subprocess, sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = pathlib.Path(__file__).resolve().parent.parent
ARCH = ROOT / "01-sources-archive"
H = ROOT / "03-harness"
FAILS = []


def check(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" - {detail}" if detail else ""))
    if not ok:
        FAILS.append(name)


# 1 - integrity
r = subprocess.run([sys.executable, str(H / "verify.py")], capture_output=True, text=True)
check("every source captured and hashing clean", r.returncode == 0,
      "" if r.returncode == 0 else "run verify.py to see which")

# 2 - wayback
prov = ARCH / "PROVENANCE.md"
cfg = json.loads((ARCH / "sources.json").read_text(encoding="utf-8"))


def section(text, sid):
    # The provenance block for one source, bounded by the next `## ` header or EOF, so an
    # unbounded match cannot reach into a later source and report a missing citation as present.
    m = re.search(rf"## `{re.escape(sid)}`.*?(?=\n## |\Z)", text, re.S)
    return m.group(0) if m else ""


if prov.exists():
    text = prov.read_text(encoding="utf-8")
    missing = [s["id"] for s in cfg["sources"]
               if not re.search(r"^- Wayback: <http", section(text, s["id"]), re.M)]
    check("every source has a Wayback citation", not missing,
          "" if not missing else f"{len(missing)} without one: {', '.join(missing[:4])}")
else:
    check("every source has a Wayback citation", False, "PROVENANCE.md does not exist")

# 3 - reproduction
b = subprocess.run([sys.executable, str(H / "build.py"), "--check"], capture_output=True, text=True)
check("every headline figure reproduces from the committed data", b.returncode == 0,
      "" if b.returncode == 0 else "run build.py --check to see which drifted")

# 4 - derived data newer than the sources it draws from
derived = ROOT / "02-data" / "headline_figures.csv"
raw = ARCH / "raw"
if derived.exists() and raw.exists():
    newest_src = max((p.stat().st_mtime for p in raw.rglob("*") if p.is_file()), default=0)
    check("derived data is newer than the sources it derives from",
          derived.stat().st_mtime >= newest_src, "re-run build.py")
else:
    check("derived data is newer than the sources it derives from", False,
          "headline_figures.csv or 01-sources-archive/raw is missing")

# 5 - corrections ledger
check("corrections ledger exists", (ROOT / "CORRECTIONS.md").exists())

print()
if FAILS:
    print(f"NOT CLEAR TO PUBLISH. {len(FAILS)} check(s) failed:")
    for f in FAILS:
        print(f"  - {f}")
    print("\nFix them. There is no override.")
    sys.exit(1)
print("CLEAR TO PUBLISH. Every source captured, hashed, cited, and every figure reproduces.")
