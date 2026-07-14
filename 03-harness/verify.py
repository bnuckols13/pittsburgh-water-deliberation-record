#!/usr/bin/env python3
"""
verify.py - re-hash every archived source and check it against its recorded hash.

This is the integrity check a reader runs. No network, no keys. If it prints OK for a
source, the file in this repo is byte-for-byte the file that was captured, and the figures
that cite it trace to something that has not changed under it.

    python 03-harness/verify.py

Exit 0 = every listed source is present and hashes clean.
Exit 1 = a hash changed, a file is missing, or a source was never captured.
"""
import hashlib, json, pathlib, sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = pathlib.Path(__file__).resolve().parent.parent
ARCH = ROOT / "01-sources-archive"


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main():
    cfg = json.loads((ARCH / "sources.json").read_text(encoding="utf-8"))
    ok = missing = bad = 0
    file_sources = [s for s in cfg["sources"] if s.get("mode") == "file"]
    for s in file_sources:
        p = ARCH / s["path"]
        side = p.with_suffix(p.suffix + ".sha256")
        if not p.exists():
            print(f"NOT CAPTURED  {s['id']}  ({s['path']})")
            missing += 1
            continue
        if not side.exists():
            print(f"NO SIDECAR    {s['id']}  cannot verify without a recorded hash")
            bad += 1
            continue
        recorded = side.read_text(encoding="utf-8").split()[0]
        actual = sha256(p)
        if recorded == actual:
            print(f"OK            {s['id']}  {actual[:16]}...")
            ok += 1
        else:
            print(f"HASH MISMATCH {s['id']}")
            print(f"              recorded {recorded}")
            print(f"              actual   {actual}")
            bad += 1
    print(f"\n{ok} verified, {missing} not captured, {bad} failed.")
    if bad:
        print("A mismatch means the file changed after capture. Treat the analysis as unsound until resolved.")
    if missing:
        print("Run `python 03-harness/capture.py` on a machine with network access.")
    return 0 if (bad == 0 and missing == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
