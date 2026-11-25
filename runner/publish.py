"""Veröffentlichung: staging aufbauen, schwärzen, Repo anlegen, pushen, Release.

Wird erst nach Abschluss von Auswertung + Privacprüfung ausgeführt.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGE = ROOT / "publish"
REPO_NAME = "strata-hotrod-bench-rtx3090-96gb-windows"


def run(cmd, cwd=None, check=True):
    print("RUN:", " ".join(str(c) for c in cmd), flush=True)
    r = subprocess.run([str(c) for c in cmd], cwd=cwd, capture_output=True, text=True)
    if r.returncode and check:
        print(r.stdout[-2000:]); print(r.stderr[-2000:])
        raise SystemExit(f"Befehl fehlgeschlagen: {cmd[0]}")
    return r


def build_stage() -> None:
    if STAGE.exists():
        def force_remove(func, path, _exc):
            import os
            os.chmod(path, 0o666)
            func(path)
        for child in STAGE.iterdir():
            if child.name == ".git":
                continue  # keep repository history
            if child.is_dir():
                shutil.rmtree(child, onerror=force_remove)
            else:
                child.unlink()
    for d in ("results", "charts", "runner", "prompts", "logs", "outreach", "configs",
              "telemetry", "dashboard"):
        (STAGE / d).mkdir(parents=True, exist_ok=True)

    copy = [
        ("README.md", STAGE / "README.md"),
        ("DECISIONS.md", STAGE / "DECISIONS.md"),
        ("FLAGS.md", STAGE / "FLAGS.md"),
        ("PRIVACY_CHECK.md", STAGE / "PRIVACY_CHECK.md"),
        ("STATE.md", STAGE / "STATE.md"),
        ("RESTORE_REPORT.md", STAGE / "RESTORE_REPORT.md"),
        ("TELEMETRY.md", STAGE / "TELEMETRY.md"),
        ("HANDOFF.md", STAGE / "HANDOFF.md"),
        ("docs/RESULTS_TABLES.md", STAGE / "docs" / "RESULTS_TABLES.md"),
        ("docs/KILLED_PROCESSES.md", STAGE / "docs" / "KILLED_PROCESSES.md"),
    ]
    for src, dst in copy:
        s = ROOT / src
        if s.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(s, dst)

    for pattern, target in (("results/*.csv", "results"), ("results/*.json", "results"),
                            ("charts/*.png", "charts"), ("runner/*.py", "runner"),
                            ("runner/matrix.yaml", "runner"), ("runner/mini_matrix.yaml", "runner"),
                            ("prompts/*", "prompts"), ("configs/*.json", "configs"),
                            ("telemetry/*.jsonl", "telemetry"), ("telemetry/*.json", "telemetry"),
                            ("dashboard/*.html", "dashboard"),
                            ("outreach/*.md", "outreach"),
                            ("outreach/community-report/*", "outreach/community-report")):
        (STAGE / target).mkdir(parents=True, exist_ok=True)
        for f in ROOT.glob(pattern):
            if f.is_file():
                shutil.copy2(f, STAGE / target / f.name)

    # Log-Archiv (gezippt; Privacy-Skript bearbeitet txt-Dateien vorher).
    logzip = STAGE / "logs" / "logs.zip"
    with zipfile.ZipFile(logzip, "w", zipfile.ZIP_DEFLATED) as z:
        for f in ROOT.glob("logs/*.log"):
            if f.is_file():
                z.write(f, f.name)
    (STAGE / "LICENSE").write_text(
        "MIT License\n\nCopyright (c) 2026 [USER]\n\n"
        "Permission is hereby granted, free of charge, to any person obtaining a copy...\n",
        encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage-only", action="store_true")
    ap.add_argument("--repo", default=REPO_NAME)
    opts = ap.parse_args(argv)

    build_stage()
    print(f"Stage gebaut: {STAGE}")
    if opts.stage_only:
        return 0

    # 1. Privacy (schwaerzt Stage; bei Rest-Treffer Exit 1 -> kein Push)
    r = run([sys.executable, ROOT / "runner" / "privacy.py"], check=False)
    if r.returncode:
        print("Datenschutzprüfung fehlgeschlagen — KEIN Upload.")
        return 1

    # 2. Repo anlegen (falls vorhanden: wiederverwenden)
    user = run(["gh", "api", "user", "--jq", ".login"]).stdout.strip()
    check = subprocess.run(["gh", "repo", "view", f"{user}/{opts.repo}"],
                           capture_output=True, text=True)
    if check.returncode:
        run(["gh", "repo", "create", opts.repo, "--public", "--description",
             "Strata-HotRod Benchmark auf RTX 3090 24GB / 96GB RAM / Windows 10"])
    else:
        print(f"Repo {user}/{opts.repo} existiert bereits — verwende es.")

    # 3. Commit + Push
    run(["git", "init", "-b", "main"], cwd=STAGE)
    run(["git", "config", "user.name", "[USER]"], cwd=STAGE)
    run(["git", "config", "user.email", "[USER]@users.noreply.github.com"], cwd=STAGE)
    run(["git", "add", "-A"], cwd=STAGE)
    run(["git", "commit", "-m", "Initial benchmark results: Strata-HotRod IQ3_S on RTX 3090"], cwd=STAGE)
    run(["git", "remote", "add", "origin", f"https://github.com/{user}/{opts.repo}.git"], cwd=STAGE)
    run(["git", "push", "-u", "origin", "main"], cwd=STAGE)

    # 4. Release mit Zip
    zip_path = STAGE / "results" / "strata-hotrod-bench-results.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in (STAGE / "results").glob("*"):
            if f.is_file() and f != zip_path:
                z.write(f, "results/" + f.name)
        for f in (STAGE / "charts").glob("*.png"):
            z.write(f, "charts/" + f.name)
        for f in (STAGE / "telemetry").glob("*"):
            if f.is_file():
                z.write(f, "telemetry/" + f.name)
        for f in (STAGE / "dashboard").glob("*.html"):
            z.write(f, "dashboard/" + f.name)
    run(["gh", "release", "create", "v1.0", str(zip_path), "--title", "v1.0 — Benchmark-Ergebnisse",
         "--notes", "Vollständige Ergebnisdateien, Diagramme und Runner."], cwd=STAGE)

    # 5. Verify
    view = run(["gh", "repo", "view", f"{user}/{opts.repo}", "--json",
                "url,visibility,isPrivate"], cwd=STAGE)
    print("REPO:", view.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
