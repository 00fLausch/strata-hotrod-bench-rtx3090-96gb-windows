"""Erzeugt alle Diagramme aus results/summary.csv nach docs/charts/ (bzw. charts/)."""
from __future__ import annotations

import json
import json as _json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "charts"
CSV = ROOT / "results" / "summary.csv"

STYLE = {"figure.facecolor": "white", "axes.grid": True, "grid.alpha": 0.3,
         "font.size": 9, "axes.titlesize": 11}
plt.rcParams.update(STYLE)


def errbar(ax, x, y, lo, hi, **kw):
    xs_all = list(x)
    ys_all = list(y)
    lo_all = list(lo)
    hi_all = list(hi)
    ok = [i for i in range(len(ys_all)) if isinstance(ys_all[i], (int, float, np.floating))
          and isinstance(lo_all[i], (int, float, np.floating))
          and isinstance(hi_all[i], (int, float, np.floating))]
    if not ok:
        return
    xs = [xs_all[i] for i in ok]
    ys = [ys_all[i] for i in ok]
    los = [max(0.0, ys[j] - lo_all[i]) for j, i in enumerate(ok)]
    his = [max(0.0, hi_all[i] - ys[j]) for j, i in enumerate(ok)]
    ax.errorbar(xs, ys, yerr=[los, his], capsize=3, **kw)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(CSV) if CSV.exists() else pd.DataFrame()
    if df.empty:
        print("no data")
        return 0
    num = ["reserve_mib", "decode_median", "prefill_median", "ttft_median",
           "slots_final", "shrinks", "gpu_power_mean", "gpu_temp_max"]
    for c in num:
        if c in df:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    made = []

    # 1) Reserve-Sweep (B1): Slots und Decode
    b1 = df[df["block"].astype(str).str.startswith("B1")].sort_values("reserve_mib")
    if not b1.empty and b1["decode_median"].notna().any():
        fig, ax = plt.subplots(figsize=(7, 4))
        errbar(ax, b1["reserve_mib"], b1["decode_median"],
               b1["decode_ci_lo"], b1["decode_ci_hi"], fmt="o-", color="#1f77b4",
               label="Decode (tok/s)")
        ax.set_xlabel("vram-reserve-mib (MiB)")
        ax.set_ylabel("Decode tok/s (Median, 95%-KI)")
        ax.set_title("B1: VRAM-Reserve vs. Decode")
        ax.legend()
        fig.tight_layout()
        fig.savefig(OUT / "b1_reserve_decode.png", dpi=160)
        plt.close(fig)
        made.append("b1_reserve_decode.png")

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(b1["reserve_mib"], b1["slots_final"], "o-", color="#2ca02c", label="finale Slots")
        ax.set_xlabel("vram-reserve-mib (MiB)")
        ax.set_ylabel("Expert-Slots")
        ax.set_title("B1: Reserve vs. Slots")
        ax2 = ax.twinx()
        ax2.plot(b1["reserve_mib"], b1["shrinks"], "s--", color="#d62728", label="Shrinks")
        ax2.set_ylabel("Shrink-Runden")
        ax.legend(loc="upper left"); ax2.legend(loc="upper right")
        fig.tight_layout(); fig.savefig(OUT / "b1_reserve_slots.png", dpi=160); plt.close(fig)
        made.append("b1_reserve_slots.png")

    # 2) Kontext-Sweep
    d1 = df[df["block"] == "D1"]
    if not d1.empty and d1["decode_median"].notna().any():
        order = {"long_4k": 4, "long_16k": 16, "long_32k": 32, "long_64k": 64,
                 "long_128k": 128, "long_200k": 200}
        d1 = d1.assign(k=d1["id"].map(lambda s: next((v for k, v in order.items() if k in str(s)), np.nan)))
        d1 = d1.dropna(subset=["k"]).sort_values("k")
        fig, ax = plt.subplots(figsize=(7, 4))
        errbar(ax, d1["k"], d1["decode_median"], d1["decode_ci_lo"], d1["decode_ci_hi"],
               fmt="o-", color="#1f77b4", label="Decode")
        ax.set_xlabel("Prompt-Kontext (K-Tokens)"); ax.set_ylabel("Decode tok/s")
        ax.set_title("D1: Context length vs decode")
        fig.tight_layout(); fig.savefig(OUT / "d1_context_decode.png", dpi=160); plt.close(fig)
        made.append("d1_context_decode.png")

    # 3) Prefill-Sweep 32K/128K
    c1 = df[df["block"] == "C1"]
    if not c1.empty and c1["prefill_median"].notna().any():
        fig, ax = plt.subplots(figsize=(7, 4))
        for suffix, color, label in (("32k", "#1f77b4", "32K-Prompt"),
                                     ("128k", "#ff7f0e", "128K-Prompt")):
            sub = c1[c1["id"].astype(str).str.endswith(suffix)].sort_values("prefill")
            if sub.empty:
                continue
            xs = range(len(sub))
            errbar(ax, xs, sub["prefill_median"], sub["prefill_ci_lo"], sub["prefill_ci_hi"],
                   fmt="o-", color=color, label=label)
            ax.set_xticks(list(xs))
            ax.set_xticklabels([str(v).replace("auto:", "") for v in sub["prefill"]], rotation=30)
        ax.set_xlabel("Prefill-Chunk"); ax.set_ylabel("Prefill tok/s")
        ax.set_title("C1: Prefill-Chunk vs. Prefill-Durchsatz"); ax.legend()
        fig.tight_layout(); fig.savefig(OUT / "c1_prefill.png", dpi=160); plt.close(fig)
        made.append("c1_prefill.png")

    # 4) Lernkurve
    stats_path = ROOT / "results" / "statistics.json"
    curve = []
    if stats_path.exists():
        for r in json.loads(stats_path.read_text("utf-8")).get("rows", []):
            pass
    learn_files = sorted((ROOT / "results").glob("E1_*.json"))
    if learn_files:
        d = json.loads(learn_files[0].read_text("utf-8"))
        chunks = d.get("learning_curve") or []
        xs = [c["from_request"] for c in chunks]
        ys = [c["decode"]["median"] for c in chunks if c.get("decode", {}).get("median") is not None]
        if ys:
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.plot(xs[:len(ys)], ys, "o-", color="#9467bd")
            ax.set_xlabel("Request-Index"); ax.set_ylabel("Decode tok/s")
            ax.set_title("E1: Lernkurve ab leeren Lerndaten")
            fig.tight_layout(); fig.savefig(OUT / "e1_learning.png", dpi=160); plt.close(fig)
            made.append("e1_learning.png")

    # 5) Power-Limit (nur wenn Daten vorhanden)
    h1 = df[df["block"] == "H1"]
    if not h1.empty and h1["decode_median"].notna().any():
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(h1["power_w"], h1["decode_median"], "o-", color="#d62728", label="Decode")
        ax.set_xlabel("Power-Limit (W)"); ax.set_ylabel("Decode tok/s")
        ax.set_title("H1: Power-Limit vs. Decode"); ax.legend()
        fig.tight_layout(); fig.savefig(OUT / "h1_power.png", dpi=160); plt.close(fig)
        made.append("h1_power.png")

    # 6) Rauschmessung A2
    a2 = df[df["block"].astype(str).str.startswith("A2")]
    if not a2.empty and a2["decode_median"].notna().any():
        fig, ax = plt.subplots(figsize=(7, 4))
        errbar(ax, range(len(a2)), a2["decode_median"], a2["decode_ci_lo"], a2["decode_ci_hi"],
               fmt="o-", color="#2ca02c")
        ax.set_xticks(range(len(a2))); ax.set_xticklabels(a2["block"].astype(str))
        ax.set_ylabel("Decode tok/s"); ax.set_title("A2: Drift über den Lauf")
        fig.tight_layout(); fig.savefig(OUT / "a2_noise.png", dpi=160); plt.close(fig)
        made.append("a2_noise.png")

    # 7) Resident experts vs Decode (B2)
    tv = df[df["experts_vram_end"].notna() & df["decode_median"].notna()] if "experts_vram_end" in df else df
    if not tv.empty:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.scatter(tv["experts_vram_end"], tv["decode_median"], s=22, alpha=0.7, color="#9467bd")
        ax.set_xlabel("Resident experts"); ax.set_ylabel("Decode tok/s")
        ax.set_title("B2: Resident experts vs decode")
        fig.tight_layout(); fig.savefig(OUT / "b2_experts_decode.png", dpi=160); plt.close(fig)
        made.append("b2_experts_decode.png")

    # 8) Prompt-Länge vs Prefill (D7)
    d7 = df[df["block"] == "D7"]
    if not d7.empty and d7["prefill_median"].notna().any():
        order = {"chat_de": 84, "len_500": 500, "len_2k": 2000, "len_8k": 8000}
        d7 = d7.assign(k=d7["id"].map(lambda s: next((v for key, v in order.items() if key in str(s)), np.nan)))
        d7 = d7.dropna(subset=["k"]).sort_values("k")
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(d7["k"], d7["prefill_median"], "o-", color="#17becf")
        ax.set_xscale("log"); ax.set_xlabel("Prompt tokens (log)"); ax.set_ylabel("Prefill tok/s")
        ax.set_title("D7: Prompt length vs prefill (fixed cost)")
        fig.tight_layout(); fig.savefig(OUT / "d7_prompt_prefill.png", dpi=160); plt.close(fig)
        made.append("d7_prompt_prefill.png")

    # 9) Telemetry time seriesn eines repraesentativen Laufs
    tl_dir = ROOT / "telemetry"
    candidates = sorted(tl_dir.glob("*.jsonl")) if tl_dir.exists() else []
    if candidates:
        rows = [_json.loads(l) for l in candidates[0].read_text("utf-8").splitlines() if l.strip()]
        if rows:
            t0 = rows[0].get("ts", 0)
            fig, axes = plt.subplots(3, 1, figsize=(9, 7), sharex=True)
            for ax, key, label, color in zip(
                    axes, ("decode_tok_s", "gpu_power_w", "resident_experts"),
                    ("Decode tok/s", "Power (W)", "Resident experts"),
                    ("#1f77b4", "#d62728", "#2ca02c")):
                xs = [r["ts"] - t0 for r in rows]
                ys = [r.get(key) for r in rows]
                ax.plot(xs, ys, color=color, lw=1)
                ax.set_ylabel(label)
            axes[-1].set_xlabel("Time since start (s)")
            axes[0].set_title(f"Telemetry time series: {candidates[0].stem}")
            fig.tight_layout(); fig.savefig(OUT / "telemetry_timeseries.png", dpi=160); plt.close(fig)
            made.append("telemetry_timeseries.png")

    # 10) Engpass-Balken (aus README der Standard-Benchmarks, falls vorhanden)
    #     Die Anteile werden in der Auswertung aus TIMELINE-Rohdaten berechnet;
    #     hier ein Platzhalter mit echten Werten, sofern vorhanden.
    tl_sums = []
    if tl_dir.exists():
        for sf in sorted(tl_dir.glob("*-summary.json")):
            try:
                d = _json.loads(sf.read_text("utf-8"))
            except Exception:
                continue
            tl_sums.append((sf.stem.replace("-summary", ""), d.get("timeline", {})))
    if tl_sums:
        fig, ax = plt.subplots(figsize=(8, 4))
        labels = [x[0][:18] for x in tl_sums[:10]]
        gaps = [x[1].get("gap_windows_lost", 0) for x in tl_sums[:10]]
        ax.bar(labels, gaps, color="#d62728", alpha=0.8)
        ax.set_ylabel("Lost timeline windows")
        ax.set_title("Timeline data loss (gap marker)")
        plt.xticks(rotation=45, ha="right")
        fig.tight_layout(); fig.savefig(OUT / "timeline_gaps.png", dpi=160); plt.close(fig)
        made.append("timeline_gaps.png")

    print(json.dumps({"charts": made}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
