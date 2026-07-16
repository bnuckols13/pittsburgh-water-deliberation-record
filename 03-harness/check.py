#!/usr/bin/env python3
"""
check.py - the one command a reader runs.

It confirms the archive is intact and that the numbers reproduce, then prints a single
verdict. Nothing here needs a network or a private key.

    python 03-harness/check.py

It runs, in order:
    verify.py          re-hash every archived source against its recorded hash
    build.py --check   recompute every headline figure in a throwaway dir and confirm it reproduces

Exit 0 = trustworthy: sources hash clean and every figure reproduces from the committed data.
Exit 1 = something did not check out; the detail is printed above the verdict.
"""
import pathlib, subprocess, sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

H = pathlib.Path(__file__).resolve().parent
PY = sys.executable


def run(script, *args):
    r = subprocess.run([PY, str(H / script), *args], capture_output=True, text=True)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).rstrip()


def main():
    print("Checking the archive. Nothing here needs a network or a private key.\n")

    print("--- source integrity (verify.py) " + "-" * 26)
    v_rc, v_out = run("verify.py")
    print(v_out)

    print("\n--- reproduction (build.py --check) " + "-" * 23)
    b_rc, b_out = run("build.py", "--check")
    print(b_out)

    print("\n--- database (build_db.py --check) " + "-" * 24)
    d_rc, d_out = run("build_db.py", "--check")
    print(d_out)

    ok = (v_rc == 0 and b_rc == 0 and d_rc == 0)
    print("\n" + "=" * 60)
    if ok:
        print("TRUSTED. Every source hashes clean and every headline figure reproduces")
        print("from the committed data. You did not have to trust the reporter to")
        print("establish any of that.")
    else:
        print("NOT CLEAN. A check above failed. Read it, and do not rely on the figures")
        print("until it resolves.")
    print("=" * 60)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
