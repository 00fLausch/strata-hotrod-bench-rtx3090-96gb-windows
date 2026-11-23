"""Erzeugt den versionierten, reproduzierbaren Prompt-Satz fuer den Benchmark.

Jeder Prompt hat eine stabile ID, einen festen Seed und einen SHA-256 ueber den
exakten Text. Langkontext-Prompts werden deterministisch aus einem Grundtext
plus eindeutigem Tag erzeugt; die tatsaechliche Token-Zahl misst der Server bei
jedem Request und wird in den Ergebnissen gespeichert.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "prompts" / "prompts.json"

SHORT = {
    "chat_de": (
        "Erklaere in drei kurzen Absaetzen, warum ein Mixture-of-Experts-Modell auf "
        "einer einzelnen Consumer-Grafikkarte langsamer sein kann als ein dichtes Modell "
        "aequaler Qualitaet. Nenne zwei konkrete Engpaesse."
    ),
    "chat_en": (
        "In three short paragraphs, explain why a mixture-of-experts model on a single "
        "consumer GPU can be slower than a dense model of equal quality. Name two concrete "
        "bottlenecks."
    ),
    "coding": (
        "Write a complete Python 3.11 module `cache.py`: an async TTL cache with `get`, "
        "`set`, `delete`, `clear`, thread-safe locking, type hints, docstrings, and six "
        "unittest test cases. Output only the code, no prose."
    ),
    "math_reasoning": (
        "A train leaves A at 09:00 at 60 km/h. A second leaves B at 09:30 at 80 km/h toward A. "
        "The distance AB is 350 km. At what time and where do they meet? Show the equations, "
        "then give the final answer in one sentence."
    ),
    "json_task": (
        "Return ONLY valid JSON, no markdown: an object with keys 'name' (string), "
        "'n' (integer, 42), 'items' (array of three strings), and 'ok' (boolean true)."
    ),
    "tool_call": (
        "You have a tool `get_weather(city: str)`. The user asks: 'What is the weather in Berlin?' "
        "Reply with a single tool call to get_weather with the correct argument. Do not answer "
        "the weather question yourself."
    ),
}

LONG_BASE = (
    "Die Schichten eines Mixture-of-Experts-Modellers wechseln routingscharf zwischen "
    "Experten, deren Gewichte teils auf der Grafikkarte, teils im Arbeitsspeicher und "
    "teilweise auf einer SSD liegen. Bei jeder Anfrage werden fuer jedes Token nur wenige "
    "von vielen Experten ausgewaehlt; die Auswahl muss berechnet, die Gewichte muessen "
    "geladen und die Ergebnisse muessen wieder zusammengefuehrt werden. Auf Windows mit "
    "WDDM konkurrieren Treiber, Desktop und Anwendungen um denselben Speicher. "
)

# Ziel-Token-Zahlen; der Server meldet die tatsaechliche Zahl pro Request.
LONG_TARGETS = {
    "len_500": 450,
    "len_2k": 1900,
    "len_8k": 7800,
    "long_4k": 3800,
    "long_16k": 15500,
    "long_32k": 31000,
    "long_64k": 62000,
    "long_128k": 118000,
    "long_200k": 190000,
}

# ~4.2 Zeichen pro Token als Startschaetzung fuer deutschen Fliesstext.
CHARS_PER_TOKEN = 4.2


def add_tag(base: str, tag: str, target_tokens: int) -> str:
    unit = f"{LONG_BASE}[tag={tag}] "
    n = max(1, int(target_tokens * CHARS_PER_TOKEN / len(unit)))
    text = unit * n
    # Eindeutiger Abschluss, damit Cache-Wiederverwendung kontrollierbar ist.
    return f"{text}\nFRAGE: Nenne die erste Zeile dieses Textes und antworte mit OK."


def main() -> int:
    prompts = []
    for pid, text in SHORT.items():
        prompts.append({
            "id": pid,
            "text": text,
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "target_tokens": None,
            "kind": "short",
        })
    for pid, target in LONG_TARGETS.items():
        text = add_tag(LONG_BASE, pid, target)
        prompts.append({
            "id": pid,
            "text": text,
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "target_tokens": target,
            "kind": "long",
        })
    payload = {
        "version": "1.0",
        "created": "2026-11-23",
        "note": "Feste Prompts, feste Seeds, feste Ausgabelänge. Token-Ziele sind Naeherung; gemessen wird usage.prompt_tokens.",
        "seeds": {"default": 20261123, "alt": 424242},
        "max_tokens": {"short": 128, "long": 16, "quality": 384},
        "prompts": prompts,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    (OUT.with_suffix(".sha256")).write_text(manifest + "\n", encoding="ascii")
    print(json.dumps({"out": str(OUT), "manifest_sha256": manifest,
                      "count": len(prompts)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
