"""Auswertung aller results/*.json -> summary.csv, statistics.json, RESULTS_TABLES.md.

Robust gegen unterschiedliche Test-Arten (http, command, learning, concurrent, soak, error).
"""
from __future__ import annotations

import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats as scipy_stats

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
DOCS = ROOT / "docs"
SEED = 20261123


def load_all():
    rows = []
    for f in sorted(RESULTS.glob("*.json")):
        if f.name.startswith("MINI_") or f.name in ("summary.json", "statistics.json"):
            continue
        try:
            d = json.loads(f.read_text("utf-8"))
        except ValueError:
            continue
        if not isinstance(d, dict):
            continue
        rows.append(d)
    return rows


def g(d, *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
        if cur is None:
            return default
    return cur


def med(d, key):
    v = g(d, "summary", key, "median")
    if v is not None:
        return float(v)
    vals = [r.get(key) for r in (d.get("records") or []) if isinstance(r, dict)]
    vals = [float(v) for v in vals if isinstance(v, (int, float)) and math.isfinite(v)]
    return float(np.median(vals)) if vals else None


def ci(d, key):
    lo = g(d, "summary", key, "ci95_low")
    hi = g(d, "summary", key, "ci95_high")
    return (lo, hi) if lo is not None and hi is not None else (None, None)


def bootstrap(vals):
    vals = [float(v) for v in vals if isinstance(v, (int, float)) and math.isfinite(v)]
    if len(vals) < 2:
        return (None, None)
    rng = np.random.default_rng(SEED)
    boots = np.median(rng.choice(vals, size=(10000, len(vals)), replace=True), axis=1)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return (round(float(lo), 3), round(float(hi), 3))


def extract(d):
    spec = d.get("spec") or {}
    args = spec.get("args") or {}
    env = spec.get("env") or {}
    startup = d.get("startup") or {}
    facts = d.get("engine_facts_after") or {}
    request = spec.get("request") or {}
    return {
        "id": d.get("test_id", ""),
        "block": d.get("block", ""),
        "priority": d.get("priority", ""),
        "label": d.get("label", ""),
        "status": d.get("status", ""),
        "reserve_mib": args.get("--vram-reserve-mib", 512),
        "prefill": args.get("--prefill", "auto:16384"),
        "kv": args.get("--kv", "int8"),
        "max_context": args.get("--max-context", 131072),
        "special": d.get("special", ""),
        "power_w": spec.get("watts", ""),
        "n": g(d, "summary", "decode_tps", "n") or len(d.get("records") or []),
        "decode_median": round(med(d, "decode_tps"), 3) if med(d, "decode_tps") is not None else None,
        "decode_q1": g(d, "summary", "decode_tps", "q1"),
        "decode_q3": g(d, "summary", "decode_tps", "q3"),
        "decode_ci_lo": ci(d, "decode_tps")[0],
        "decode_ci_hi": ci(d, "decode_tps")[1],
        "prefill_median": round(med(d, "prefill_tps"), 3) if med(d, "prefill_tps") is not None else None,
        "prefill_ci_lo": ci(d, "prefill_tps")[0],
        "prefill_ci_hi": ci(d, "prefill_tps")[1],
        "ttft_median": g(d, "summary", "ttft_s", "median"),
        "ttft_ci_lo": ci(d, "ttft_s")[0],
        "ttft_ci_hi": ci(d, "ttft_s")[1],
        "slots_auto": startup.get("auto_slots"),
        "slots_final": startup.get("final_slots") or facts.get("expert_slots"),
        "shrinks": startup.get("shrink_rounds"),
        "vram_free_after": startup.get("free_mib_after_load") or facts.get("vram_free_mib"),
        "expert_cache_mib": facts.get("expert_cache_mib"),
        "disk_read_delta_mb": d.get("disk_read_delta_mb"),
        "gpu_power_mean": g(d, "gpu", "power_w_mean"),
        "gpu_temp_max": g(d, "gpu", "temp_c_max"),
        "gpu_util_mean": g(d, "gpu", "util_pct_mean"),
        "pcie_gen": facts.get("pcie_gen"),
        "warmup_wall": g(d, "warmup", "wall_s"),
        "request_tokens": med(d, "prompt_tokens"),
        "experts_vram_start": g(d, "telemetry", "experts", "resident_start"),
        "experts_vram_end": g(d, "telemetry", "experts", "resident_end"),
        "experts_total": g(d, "telemetry", "experts", "total"),
        "swaps_start": g(d, "telemetry", "experts", "swaps_start"),
        "swaps_end": g(d, "telemetry", "experts", "swaps_end"),
        "rounds_start": g(d, "telemetry", "experts", "rounds_start"),
        "rounds_end": g(d, "telemetry", "experts", "rounds_end"),
        "swaps_per_round": g(d, "telemetry", "experts", "swaps_per_round"),
        "record_on": g(d, "telemetry", "record_actually_on"),
        "tele_samples": g(d, "telemetry", "samples"),
        "tele_vram_used_mib_mean": g(d, "telemetry", "series", "vram_used", "mean"),
        "tele_gpu_power_w_mean": g(d, "telemetry", "series", "gpu_power_w", "mean"),
        "tele_disk_read_mean": g(d, "telemetry", "series", "disk_read_mb", "mean"),
        "tele_timeline_windows": g(d, "telemetry", "timeline", "windows"),
        "tele_timeline_gaps": g(d, "telemetry", "timeline", "gaps"),
        "errors": len(d.get("errors") or [r.get("error") for r in (d.get("records") or []) if r.get("error")]),
    }


def compare_groups(rows, block_a, block_b, key="decode_median"):
    a = [r[key] for r in rows if r["block"] == block_a and r[key] is not None
         and r["decode_ci_lo"] is not None and r["decode_ci_hi"] is not None]
    b = [r[key] for r in rows if r["block"] == block_b and r[key] is not None
         and r["decode_ci_lo"] is not None and r["decode_ci_hi"] is not None]
    if len(a) < 2 or len(b) < 2:
        return {"n_a": len(a), "n_b": len(b), "verdict": "zu wenig Daten"}
    try:
        _, p = scipy_stats.mannwhitneyu(a, b, alternative="two-sided")
    except ValueError:
        p = None
    # NCI ueber die Einzel-KIs: konservativ
    ais = [r for r in rows if r["block"] == block_a and r[key] is not None]
    bis = [r for r in rows if r["block"] == block_b and r[key] is not None]
    alo = min((r["decode_ci_lo"] for r in ais if r["decode_ci_lo"] is not None), default=None)
    ahi = max((r["decode_ci_hi"] for r in ais if r["decode_ci_hi"] is not None), default=None)
    blo = min((r["decode_ci_lo"] for r in bis if r["decode_ci_lo"] is not None), default=None)
    bhi = max((r["decode_ci_hi"] for r in bis if r["decode_ci_hi"] is not None), default=None)
    overlap = not (alo is not None and blo is not None and (ahi < blo or bhi < alo))
    if not overlap:
        verdict = "signifikant (KIs ueberlappen nicht)"
    elif p is not None and p < 0.05:
        verdict = "signifikant (Mann-Whitney p<0.05)"
    else:
        verdict = "kein messbarer Unterschied"
    return {"n_a": len(a), "n_b": len(b), "median_a": round(float(np.median(a)), 3),
            "median_b": round(float(np.median(b)), 3),
            "p": round(float(p), 6) if p is not None else None, "verdict": verdict}


def fmt(v, digits=2):
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.{digits}f}"
    return str(v)


def main() -> int:
    rows = [extract(d) for d in load_all()]
    for r in rows:
        # Regelbasierte Ursachenerklärung aus der Telemetrie.
        disk = r.get("tele_disk_read_mean")
        spr = r.get("swaps_per_round")
        ev = r.get("experts_vram_end")
        if disk is not None and disk < 50:
            cause = "GPU-bound: SSD-Pfad praktisch ungenutzt"
        elif disk is not None:
            cause = f"SSD-Pfad aktiv ({disk:.0f} MB/s Disk read)"
        else:
            cause = "keine Telemetrie"
        if spr is not None:
            cause += f"; {spr:.1f} Swaps/Runde"
        if ev is not None:
            cause += f"; {ev:.0f} Experten im VRAM"
        r["cause"] = cause
        try:
            if all(r.get(k) is not None for k in ("swaps_end", "swaps_start", "n", "output_tokens")):
                denom = float(r["n"]) * float(r["output_tokens"])
                if denom > 0:
                    r["swaps_per_token"] = round((float(r["swaps_end"]) - float(r["swaps_start"])) / denom, 3)
                else:
                    r["swaps_per_token"] = None
            else:
                r["swaps_per_token"] = None
        except (TypeError, ValueError):
            r["swaps_per_token"] = None

    # B2: Regression Experten im VRAM / Swaps-pro-Token gegen Decode.
    b2 = {}
    x = [r["experts_vram_end"] for r in rows if r.get("experts_vram_end") is not None and r.get("decode_median") is not None]
    y = [r["decode_median"] for r in rows if r.get("experts_vram_end") is not None and r.get("decode_median") is not None]
    if len(x) >= 5:
        slope, intercept, rv, pv, se = scipy_stats.linregress(x, y)
        b2["experts_vs_decode"] = {"n": len(x), "r": round(float(rv), 3),
                                   "r2": round(float(rv ** 2), 3), "p": round(float(pv), 6),
                                   "slope": round(float(slope), 5)}
    x2 = [r["swaps_per_token"] for r in rows if r.get("swaps_per_token") is not None and r.get("decode_median") is not None]
    y2 = [r["decode_median"] for r in rows if r.get("swaps_per_token") is not None and r.get("decode_median") is not None]
    if len(x2) >= 5:
        slope, intercept, rv, pv, se = scipy_stats.linregress(x2, y2)
        b2["swaps_per_token_vs_decode"] = {"n": len(x2), "r": round(float(rv), 3),
                                           "r2": round(float(rv ** 2), 3), "p": round(float(pv), 6),
                                           "slope": round(float(slope), 3)}
    # Statistik: Gruppe B1 (Reserve-Sweep) gegen 512 als Referenz.
    comparisons = {}
    by_block = defaultdict(list)
    for r in rows:
        by_block[r["block"]].append(r)
    ref = [r for r in rows if r["block"] == "B1_0" or r["id"] == "B1_reserve_512"]
    if ref:
        base = ref[0]
        for block in ("B1", "C1", "D1", "F1", "F2", "F3", "G2", "H1"):
            pool = [r for r in by_block.get(block, []) if r["decode_median"] is not None]
            if not pool:
                continue
            vals = [r["decode_median"] for r in pool]
            try:
                _, p = scipy_stats.mannwhitneyu(vals, [base["decode_median"]], alternative="two-sided")
            except ValueError:
                p = None
            lo, hi = bootstrap(vals)
            comparisons[block] = {
                "n": len(vals), "median": round(float(np.median(vals)), 3),
                "reference_median": base["decode_median"],
                "ci95": [lo, hi], "p": round(float(p), 6) if p is not None else None,
                "verdict": "signifikant" if (p is not None and p < 0.05) else "kein messbarer Unterschied",
            }

    # CSV
    fields = list(rows[0].keys()) if rows else ["id"]
    with (RESULTS / "summary.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    jdump = lambda obj, p: p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    jdump({"rows": rows, "comparisons": comparisons, "b2_regression": b2, "seed": SEED},
          RESULTS / "statistics.json")

    # Markdown-Tabellen
    lines = [
        "# Ergebnis-Tabellen",
        "",
        "Alle Werte: Median [IQR], 95-%-Bootstrap-KI. Decode tok/s aus Engine-Timings.",
    ]
    lines.extend([
        "",
        "| Test | Block | Reserve | Decode Median [IQR] | 95%-KI | Prefill Median | TTFT | Slots auto→final | Shrinks | Experten im VRAM | Swaps/Runde | Ursache (Telemetrie) | n | Status |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|",
    ])
    for r in rows:
        iqr = "—"
        if r["decode_q1"] is not None and r["decode_q3"] is not None:
            iqr = f"[{fmt(r['decode_q1'],1)}–{fmt(r['decode_q3'],1)}]"
        ci = f"[{fmt(r['decode_ci_lo'],1)}–{fmt(r['decode_ci_hi'],1)}]" if r["decode_ci_lo"] is not None else "—"
        slots = f"{fmt(r['slots_auto'],0)}→{fmt(r['slots_final'],0)}"
        lines.append(
            f"| {r['id']} | {r['block']} | {fmt(r['reserve_mib'],0)} | "
            f"{fmt(r['decode_median'],1)} {iqr} | {ci} | {fmt(r['prefill_median'],1)} | "
            f"{fmt(r['ttft_median'],2)} | {slots} | {fmt(r['shrinks'],0)} | "
            f"{fmt(r['experts_vram_end'],0)} | {fmt(r['swaps_per_round'],1)} | {r.get('cause','')} | "
            f"{fmt(r['n'],0)} | {r['status']} |"
        )
    lines.extend(["", "## Signifikanz (gegen B1_reserve_512)", "",
                  "| Block | n | Median | Referenz | 95%-KI | p | Urteil |", "|---|---:|---:|---:|---:|---:|---|"])
    for block, c in comparisons.items():
        lines.append(f"| {block} | {c['n']} | {c['median']} | {c['reference_median']} | "
                     f"{c['ci95']} | {fmt(c['p'],4)} | {c['verdict']} |")
    lines.extend(["", "## B2: Regression (Telemetrie)", "",
                  "| Beziehung | n | r | r² | p | Steigung |", "|---|---:|---:|---:|---:|---:|"])
    for k, v in b2.items():
        lines.append(f"| {k} | {v['n']} | {v['r']} | {v['r2']} | {fmt(v['p'],4)} | {v['slope']} |")
    lines.extend(["", "## Arbeitshypothesen", ""])
    # (a) SSD-Pfad praktisch ungenutzt?
    disk = [r["tele_disk_read_mean"] for r in rows if r.get("tele_disk_read_mean") is not None]
    a = ("bestätigt" if disk and np.median(disk) < 50 else "nicht bestätigt") if disk else "keine Daten"
    lines.append(f"- **(a) SSD-Pfad ungenutzt (96 GB RAM):** {a} "
                 f"(Median Disk read {fmt(float(np.median(disk)) if disk else None,1)} MB/s)")
    # (b) Experten im VRAM schwanken und beeinflussen Decode?
    ev = [r["experts_vram_end"] for r in rows if r.get("experts_vram_end") is not None]
    b = ("bestätigt (Streuung > 500)" if ev and (max(ev) - min(ev)) > 500 else "nicht bestätigt") if ev else "keine Daten"
    lines.append(f"- **(b) Experten im VRAM schwanken:** {b} "
                 f"(min {fmt(min(ev) if ev else None,0)}, max {fmt(max(ev) if ev else None,0)})")
    corr = b2.get("experts_vs_decode", {}).get("r")
    if corr is not None:
        lines.append(f"  - Korrelation mit Decode: r={corr} → " +
                     ("Zusammenhang messbar" if b2["experts_vs_decode"]["p"] < 0.05 else "kein messbarer Zusammenhang"))
    # (c) kurze Prompts hohe Prefill-Fixkosten?
    short = [r["prefill_median"] for r in rows if r["block"] == "D7" and r.get("prefill_median")]
    longp = [r["prefill_median"] for r in rows if r["block"] in ("C1", "D1") and r.get("prefill_median")]
    c = ("bestätigt" if short and longp and np.median(short) < 0.5 * np.median(longp)
         else "nicht bestätigt") if short and longp else "keine Daten"
    lines.append(f"- **(c) Prefill-Fixkosten bei kurzen Prompts:** {c} "
                 f"(D7 Median {fmt(float(np.median(short)) if short else None,0)} vs. Lang {fmt(float(np.median(longp)) if longp else None,0)} tok/s)")
    lines.extend(["", "## Auffälligkeiten", ""])
    # Automatische Hinweise
    stalls = [r for r in rows if r["warmup_wall"] and r["warmup_wall"] > 20]
    if stalls:
        lines.append(f"- {len(stalls)} Test(s) mit Warm-up > 20 s (Stall nach Engine-Start): " +
                     ", ".join(f"{r['id']} ({fmt(r['warmup_wall'],1)} s)" for r in stalls[:12]))
    failed = [r for r in rows if r["status"] != "complete"]
    if failed:
        lines.append(f"- {len(failed)} nicht erfolgreiche Läufe: " +
                     ", ".join(r["id"] for r in failed[:20]))
    (DOCS / "RESULTS_TABLES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(rows), "blocks": len(by_block),
                      "csv": str(RESULTS / "summary.csv"),
                      "md": str(DOCS / "RESULTS_TABLES.md")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
