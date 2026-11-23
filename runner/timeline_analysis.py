"""Engpass-Analyse aus den rohen Decode-Timeline-Fenstern.

Rechnet die gleiche Zusammenfassung wie app.js tlSummary():
GPU alone / demand reads / waits on reads in flight / CPU experts in ms und %.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
TL = ROOT / "telemetry"


def analyze(rows: list[list]) -> dict:
    """Anteile pro Decode-Fenster: Summe der Layer-Spans normative auf Fensterdauer.

    Mehrere Layer eines Fensters koennen zeitlich ueberlappen; daher werden die
    Anteile pro Fenster aus dessen Span (erster t0 bis letzter t4) und den
    gemessenen CPU-/Read-Wartezeiten gebildet und dann ueber Fenster gemittelt.
    """
    wins: dict[int, list] = {}
    for r in rows:
        if len(r) < 12:
            continue
        wins.setdefault(r[0], []).append(r)
    n = len(wins) or 1
    tot = reads = bwait = cpu = 0.0
    for wr in wins.values():
        span = (max(r[11] for r in wr) - min(r[5] for r in wr)) / 1000.0
        if span <= 0:
            continue
        rd = sum((r[9] - r[8]) / 1000.0 for r in wr if r[9] > r[8] and r[3] > 0)
        bw = sum((r[10] - r[9]) / 1000.0 for r in wr if r[10] - r[9] > 20)
        cp = sum((r[11] - r[10]) / 1000.0 for r in wr if r[4] > 0 and r[11] > r[10])
        tot += span
        reads += min(rd, span)
        bwait += min(bw, max(0.0, span - reads))
        cpu += min(cp, max(0.0, span - reads - bwait))
    tot = tot or 1
    gpu = max(0.0, tot - reads - bwait - cpu)
    return {
        "windows": len(wins),
        "rows": len(rows),
        "total_ms": round(tot, 2),
        "gpu_alone_ms": round(gpu / n, 3),
        "gpu_alone_pct": round(100 * gpu / tot, 2),
        "demand_reads_ms": round(reads / n, 3),
        "demand_reads_pct": round(100 * reads / tot, 2),
        "waits_inflight_ms": round(bwait / n, 3),
        "waits_inflight_pct": round(100 * bwait / tot, 2),
        "cpu_experts_ms": round(cpu / n, 3),
        "cpu_experts_pct": round(100 * cpu / tot, 2),
    }


def main() -> int:
    out = []
    for f in sorted(TL.glob("*-timeline.json")):
        try:
            d = json.loads(f.read_text("utf-8"))
        except ValueError:
            continue
        rows = d.get("layers") or []
        if not rows:
            continue
        a = analyze(rows)
        a["run_id"] = d.get("run_id", f.stem.replace("-timeline", ""))
        a["gaps"] = len(d.get("gaps") or [])
        out.append(a)
    if out:
        (ROOT / "results" / "bottleneck.json").write_text(
            json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        fig, ax = plt.subplots(figsize=(9, 4))
        labels = [x["run_id"][:20] for x in out[:12]]
        gpu = [x["gpu_alone_pct"] for x in out[:12]]
        reads = [x["demand_reads_pct"] for x in out[:12]]
        waits = [x["waits_inflight_pct"] for x in out[:12]]
        cpu = [x["cpu_experts_pct"] for x in out[:12]]
        ax.bar(labels, gpu, label="GPU alone / host waiting", color="#1f77b4")
        ax.bar(labels, reads, bottom=gpu, label="demand reads", color="#d62728")
        ax.bar(labels, waits, bottom=[g + r for g, r in zip(gpu, reads)],
               label="waits on reads in flight", color="#ff7f0e")
        ax.bar(labels, cpu, bottom=[g + r + w for g, r, w in zip(gpu, reads, waits)],
               label="CPU experts", color="#2ca02c")
        ax.set_ylabel("Anteil (%)"); ax.set_title("Engpass-Analyse (Decode-Timeline)")
        ax.legend(fontsize=7); plt.xticks(rotation=45, ha="right")
        fig.tight_layout()
        fig.savefig(ROOT / "charts" / "bottleneck.png", dpi=160)
        plt.close(fig)
    print(json.dumps({"analysed": len(out), "out": str(ROOT / "results" / "bottleneck.json")},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
