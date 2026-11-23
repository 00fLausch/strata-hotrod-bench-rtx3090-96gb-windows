"""Datenschutzprüfung + Schwärzung für die Veröffentlichung.

Aufruf: python runner/privacy.py [--stage DIR]
Ohne --stage wird D:\strata-bench\publish geprüft/bereinigt.
Bei einem Treffer NACH der Schwärzung wird Exit 1 zurückgegeben -> nicht veröffentlichen.
"""
from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGE = ROOT / "publish"

PATTERNS = [
    ("tailscale_ip", re.compile(r"\b100\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"), "[TAILSCALE-IP]"),
    ("local_ip", re.compile(r"\b(?:192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b"), "[LOCAL-IP]"),
    ("mac", re.compile(r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b"), "[MAC]"),
    ("hostname", re.compile(r"\bDESKTOP-[A-Z0-9]{6,}\b"), "[HOSTNAME]"),
    ("tailscale_host", re.compile(r"[a-z0-9-]+\.ts\.net\b"), "[TAILSCALE-HOST]"),
    ("username", re.compile(r"\bflauschbert\b", re.IGNORECASE), "[USER]"),
    ("email", re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"), "[EMAIL]"),
    ("api_key", re.compile(r"\b(?:[REDACTED-KEY]|[REDACTED-KEY]|[REDACTED-KEY]|sk-[A-Za-z0-9]{16,}|RShwKvZW[A-Za-z0-9]{10,})\b"), "[REDACTED-KEY]"),
    ("personal_path", re.compile(r"(?:C|D):\\Users\\[^\\\s\"']+", re.IGNORECASE), "[DRIVE]/Users/[USER]"),
]

TEXT_EXT = {".md", ".json", ".jsonl", ".txt", ".csv", ".yaml", ".yml", ".py", ".bat", ".sh", ".html", ".cfg", ".ini"}


def scan_file(path: Path, apply: bool = True) -> dict:
    try:
        text = path.read_text("utf-8")
    except (UnicodeDecodeError, OSError):
        return {"file": str(path.relative_to(ROOT)), "skipped": "binary/encoding"}
    hits = {}
    clean = text
    for name, pattern, repl in PATTERNS:
        found = pattern.findall(clean)
        if found:
            hits[name] = len(found)
            if apply:
                clean = pattern.sub(repl, clean)
    if apply and hits:
        path.write_text(clean, "utf-8")
    return {"file": str(path.relative_to(ROOT)), "hits": hits}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", type=Path, default=STAGE)
    ap.add_argument("--check-only", action="store_true")
    opts = ap.parse_args(argv)
    stage = opts.stage
    if not stage.exists():
        print(f"Stage fehlt: {stage}")
        return 1
    results = []
    for p in sorted(stage.rglob("*")):
        if p.is_file() and p.suffix.lower() in TEXT_EXT:
            results.append(scan_file(p, apply=not opts.check_only))
        elif p.is_file() and p.suffix.lower() == ".zip":
            # Zip-Inhalte werden beim Erzeugen bereits geschwärzt; hier nur_listen.
            results.append({"file": str(p.relative_to(ROOT)), "zip": True})

    # Zweiter Durchlauf: darf keine Treffer mehr finden.
    remaining = []
    for p in sorted(stage.rglob("*")):
        if p.is_file() and p.suffix.lower() in TEXT_EXT:
            r = scan_file(p, apply=False)
            if r.get("hits"):
                remaining.append(r)

    lines = ["# PRIVACY_CHECK", "",
             "Automatisierte Prüfung + Schwärzung vor der Veröffentlichung.", "",
             "## Schwärzungen (erster Durchlauf)", "",
             "| Datei | Treffer |", "|---|---|"]
    for r in results:
        if r.get("hits"):
            lines.append(f"| `{r['file']}` | {json_hits(r['hits'])} |")
    lines.extend(["", "## Verbleibende Treffer nach Schwärzung", ""])
    if remaining:
        for r in remaining:
            lines.append(f"- **{r['file']}**: {json_hits(r['hits'])}")
        lines.append("")
        lines.append("**NICHT VERÖFFENTLICHEN** – erst bereinigen.")
    else:
        lines.append("Keine. Veröffentlichung freigegeben (automatisierter Teil).")
    lines.extend(["", "## Manuelle Prüfung", "",
                  "- [ ] Keine Seriennummern in Logs/Screenshots",
                  "- [ ] Keine privaten Pfade in Prompts/Antworten",
                  "- [ ] Keine API-Keys in `.env`-Dateien oder Configs",
                  "- [ ] Keine IP-Adressen in Diagrammen (Achsenbeschriftungen)",
                  "- [ ] Keine personenbezogenen Antworttexte im Prompt-Satz"])
    (ROOT / "PRIVACY_CHECK.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (stage / "PRIVACY_CHECK.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    import json
    print(json.dumps({"scan": len(results), "redacted_files": sum(1 for r in results if r.get("hits")),
                      "remaining": len(remaining), "report": str(ROOT / "PRIVACY_CHECK.md")}, ensure_ascii=False))
    return 1 if remaining else 0


def json_hits(h: dict) -> str:
    return ", ".join(f"{k}={v}" for k, v in h.items())


if __name__ == "__main__":
    raise SystemExit(main())
