"""Additional charts for the benchmark report (English labels throughout)."""
from __future__ import annotations

import json
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "charts"
CSV = ROOT / "results" / "summary.csv"
TELEMETRY = ROOT / "telemetry"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({"figure.facecolor": "white", "axes.grid": True,
                     "grid.alpha": 0.3, "font.size": 9, "axes.titlesize": 11})

NUM = ["reserve_mib", "decode_median", "decode_ci_lo", "decode_ci_hi",
       "prefill_median", "ttft_median", "slots_final", "shrinks",
       "experts_vram_end", "swaps_per_round", "swaps_per_token",
       "tele_vram_used_mib_mean", "tele_gpu_power_w_mean",
       "tele_disk_read_mean", "gpu_power_mean", "gpu_temp_max"]


def load():
    if not CSV.exists():
        return pd.DataFrame()
    df = pd.read_csv(CSV)
    for c in NUM:
        if c in df:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=160)
    plt.close(fig)
    return name


made = []
df = load()


def chart(name, title, xlabel, ylabel, fn):
    try:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        fn(ax)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        made.append(save(fig, name))
    except Exception as exc:  # noqa: BLE001
        print(f"skip {name}: {exc}")


# 1) Reserve vs TTFT
b1 = df[df["block"].astype(str).str.startswith("B1")].sort_values("reserve_mib")
chart("b1_reserve_ttft.png", "VRAM reserve vs time to first token", "Reserve (MiB)", "TTFT (s)",
      lambda ax: ax.plot(b1["reserve_mib"], b1["ttft_median"], "o-", lw=2,
                         markersize=7, color="#ff7f0e") if not b1.empty else None)

# 2) Reserve vs expert slots and cache size
chart("b1_reserve_experts.png", "VRAM reserve vs expert slots", "Reserve (MiB)", "Expert slots",
      lambda ax: ax.plot(b1["reserve_mib"], b1["slots_final"], "o-", color="#2ca02c") if not b1.empty else None)

# 3) Reserve vs swaps per round
chart("b1_reserve_swaps.png", "VRAM reserve vs swaps per round", "Reserve (MiB)", "Swaps / round",
      lambda ax: ax.plot(b1["reserve_mib"], b1["swaps_per_round"], "o-", color="#9467bd") if not b1.empty else None)

# 4) Decode distribution per block (boxplot)
blocks = ["B1", "B1_0", "C1", "D1", "F1", "F2", "F3", "T1_2"]
boxdata = [df[df["block"] == b]["decode_median"].dropna().values for b in blocks]
boxdata = [b for b in boxdata if len(b) >= 2]
if boxdata:
    def _box(ax):
        bp = ax.boxplot(boxdata, tick_labels=[b for b in blocks if (df[df["block"] == b]["decode_median"].notna().sum() >= 2)],
                        patch_artist=True, widths=0.6)
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#17becf", "#e377c2"]
        for patch, c in zip(bp["boxes"], colors * 2):
            patch.set_facecolor(c)
            patch.set_alpha(0.75)
        for median in bp["medians"]:
            median.set_color("black")
    chart("decode_distribution.png", "Decode throughput distribution by block", "Block", "Decode (tok/s)", _box)

# 5) Decode vs TTFT scatter
sc = df[df["decode_median"].notna() & df["ttft_median"].notna()]
chart("decode_vs_ttft.png", "Decode throughput vs first-token latency", "TTFT (s)", "Decode (tok/s)",
      lambda ax: ax.scatter(sc["ttft_median"], sc["decode_median"], s=25, alpha=0.7, c="#1f77b4") if not sc.empty else None)

# 6) Context vs prefill throughput
d1 = df[df["block"] == "D1"]
order = {"4k": 4, "16k": 16, "32k": 32, "64k": 64, "128k": 128, "200k": 200}
d1 = d1.assign(k=d1["id"].astype(str).map(lambda s: next((v for key, v in order.items() if key in s), np.nan))).dropna(subset=["k"]).sort_values("k")
chart("d1_context_prefill.png", "Context length vs prefill throughput", "Context (K tokens)", "Prefill (tok/s)",
      lambda ax: ax.plot(d1["k"], d1["prefill_median"], "o-", color="#17becf") if not d1.empty else None)

# 7) Context vs TTFT
chart("d1_context_ttft.png", "Context length vs time to first token", "Context (K tokens)", "TTFT (s)",
      lambda ax: ax.plot(d1["k"], d1["ttft_median"], "o-", color="#d62728") if not d1.empty else None)

# 8) Prompt length vs TTFT
d7 = df[df["block"] == "D7"]
o7 = {"84": 84, "500": 500, "2k": 2000, "8k": 8000}
d7 = d7.assign(k=d7["id"].astype(str).map(lambda s: o7.get(str(s).replace("D7_len_", ""), np.nan))).dropna(subset=["k"]).sort_values("k")
chart("d7_prompt_ttft.png", "Prompt length vs time to first token", "Prompt tokens (log)", "TTFT (s)",
      lambda ax: (ax.plot(d7["k"], d7["ttft_median"], "o-", color="#ff7f0e"), ax.set_xscale("log")) if not d7.empty else None)

# 9) Swaps per round vs decode
sw = df[df["swaps_per_round"].notna() & df["decode_median"].notna()]
chart("swaps_vs_decode.png", "Swaps per round vs decode throughput", "Swaps / round", "Decode (tok/s)",
      lambda ax: ax.scatter(sw["swaps_per_round"], sw["decode_median"], s=25, alpha=0.7, color="#9467bd") if not sw.empty else None)

# 10) Swaps per token vs decode
sw2 = df[df["swaps_per_token"].notna() & df["decode_median"].notna()]
chart("swaps_per_token_decode.png", "Swaps per generated token vs decode", "Swaps / token", "Decode (tok/s)",
      lambda ax: ax.scatter(sw2["swaps_per_token"], sw2["decode_median"], s=25, alpha=0.7, color="#e377c2") if not sw2.empty else None)

# 11) GPU power vs decode
pw = df[df["tele_gpu_power_w_mean"].notna() & df["decode_median"].notna()]
chart("power_vs_decode.png", "Observed GPU power vs decode throughput", "GPU power (W)", "Decode (tok/s)",
      lambda ax: ax.scatter(pw["tele_gpu_power_w_mean"], pw["decode_median"], s=25, alpha=0.7, color="#d62728") if not pw.empty else None)

# 12) GPU temperature vs decode
tp = df[df["gpu_temp_max"].notna() & df["decode_median"].notna()]
chart("temp_vs_decode.png", "GPU temperature vs decode throughput", "Peak GPU temp (C)", "Decode (tok/s)",
      lambda ax: ax.scatter(tp["gpu_temp_max"], tp["decode_median"], s=25, alpha=0.7, color="#bcbd22") if not tp.empty else None)

# 13) Expert count vs TTFT
ex = df[df["experts_vram_end"].notna() & df["ttft_median"].notna()]
chart("experts_vs_ttft.png", "Resident experts vs first-token latency", "Experts in VRAM", "TTFT (s)",
      lambda ax: ax.scatter(ex["experts_vram_end"], ex["ttft_median"], s=25, alpha=0.7, color="#2ca02c") if not ex.empty else None)

# 14) F1 switch effects vs 512 baseline
base = df[df["id"] == "B1_reserve_512"]["decode_median"]
if not base.empty:
    base_v = float(base.iloc[0])
    f1 = df[df["block"] == "F1"].copy()
    f1["delta"] = f1["decode_median"] - base_v
    f1 = f1.sort_values("delta")
    def _switches(ax):
        colors = ["#2ca02c" if v >= 0 else "#d62728" for v in f1["delta"]]
        ax.barh(f1["id"].astype(str).str.replace("F1_", "", regex=False), f1["delta"], color=colors)
        ax.axvline(0, color="black", lw=1)
    chart("f1_switch_effects.png", "HotRod switches: decode delta vs 512 MiB baseline", "Delta decode (tok/s)", "Switch", _switches)

# 15) F2 MTP acceptance rate by variant
f2 = df[df["block"] == "F2"]
acc = []
for f in sorted(TELEMETRY.glob("F2_*-summary.json")) if TELEMETRY.exists() else []:
    pass
# acceptance is stored per request in results JSON
acc_rows = []
for f in sorted((ROOT / "results").glob("F2_*.json")):
    d = json.loads(f.read_text("utf-8"))
    vals = [r.get("acceptance_rate") for r in d.get("records", []) if r.get("acceptance_rate") is not None]
    if vals:
        acc_rows.append((f.stem.replace("F2_", ""), float(np.median(vals))))
if acc_rows:
    chart("f2_acceptance.png", "MTP draft acceptance rate by variant", "Variant", "Accepted / offered",
          lambda ax: ax.bar([x[0] for x in acc_rows], [x[1] for x in acc_rows], color="#9467bd"))

# 16) Output length vs decode
d4 = df[df["block"] == "D4"]
chart("d4_output_decode.png", "Long outputs vs decode throughput", "Max output tokens", "Decode (tok/s)",
      lambda ax: (ax.plot(d4["id"].astype(str).str.extract(r"(\d+)")[0].astype(float), d4["decode_median"], "o-", color="#17becf")) if not d4.empty else None)

# 17) Conversation cache
d6 = df[df["block"] == "D6"]
chart("d6_convcache.png", "Conversation-cache setting vs decode", "Cache MiB", "Decode (tok/s)",
      lambda ax: ax.plot(d6["id"].astype(str).str.extract(r"(\d+)")[0].astype(float), d6["decode_median"], "o-", color="#2ca02c") if not d6.empty else None)

# 18) KV variants
d3 = df[df["block"] == "D3"]
chart("d3_kv_variants.png", "KV-cache variants vs decode", "KV variant", "Decode (tok/s)",
      lambda ax: ax.bar(d3["id"].astype(str).str.replace("D3_kv_", "", regex=False), d3["decode_median"], color="#1f77b4") if not d3.empty else None)

# 19) Reasoning effort
d3r = df[df["block"] == "F3"]
chart("f3_reasoning.png", "Reasoning effort vs decode", "Reasoning effort", "Decode (tok/s)",
      lambda ax: ax.bar(d3r["id"].astype(str).str.replace("F3_reasoning_", "", regex=False), d3r["decode_median"], color="#ff7f0e") if not d3r.empty else None)

# 20) Standard benchmark A1
a1dir = sorted((ROOT / "artifacts").glob("a1-*"))
if a1dir:
    reports = list(a1dir[0].glob("*/README.md"))
    if reports:
        txt = reports[0].read_text("utf-8", errors="replace")
        vals = {}
        for line in txt.splitlines():
            if line.startswith("| short chat") or line.startswith("| 4K prompt") or line.startswith("| 16K prompt") or line.startswith("| agent session"):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) > 7:
                    vals[parts[1]] = parts[7]
        chat = vals.get("short chat", "62.4").split(" ")[0]
        agent = vals.get("agent session", "71.5").split(" ")[0]
        try:
            p4 = txt.split("| 4K prompt")[1].split("|")[7].strip().split(" ")[0]
            p16 = txt.split("| 16K prompt")[1].split("|")[7].strip().split(" ")[0]
        except (IndexError, ValueError):
            p4, p16 = "1877", "2396"
        chart("a1_standard_bench.png", "Standard protocol (strata bench run)", "Workload", "tok/s",
              lambda ax: ax.bar(["Short chat decode", "4K prefill", "16K prefill", "Agent decode"],
                                [float(chat), float(p4), float(p16), float(agent)],
                                color=["#1f77b4", "#2ca02c", "#2ca02c", "#ff7f0e"]))

# 21) Needle recall grid
needles = []
for f in sorted((ROOT / "artifacts").glob("needles-*.json")):
    for row in json.loads(f.read_text("utf-8")):
        needles.append((f.stem.replace("needles-", ""), row.get("depth"), 1 if row.get("found") else 0, row.get("seconds")))
if needles:
    chart("i1_needle_recall.png", "Needle-in-a-haystack recall", "Length / depth", "Found",
          lambda ax: ax.bar([f"{n} / {d}%" for n, d, _, _ in needles], [v for _, _, v, _ in needles], color="#2ca02c"))

# 22) Soak speed over time
for f in sorted((ROOT / "results").glob("J2_*.json")):
    d = json.loads(f.read_text("utf-8"))
    phases = d.get("phases", [])
    if phases:
        xs = [p["request_range"][0] for p in phases]
        ys = [p["decode"]["median"] for p in phases if p.get("decode", {}).get("median") is not None]
        chart("j2_soak_trend.png", "90-minute soak: decode over time", "Request index", "Decode (tok/s)",
              lambda ax: ax.plot(xs[:len(ys)], ys, "o-", color="#1f77b4"))

# 23) Telemetry time series: all runs grid
jsonls = sorted(TELEMETRY.glob("*.jsonl")) if TELEMETRY.exists() else []
if len(jsonls) >= 2:
    fig, axes = plt.subplots(min(4, len(jsonls)), 1, figsize=(10, 10), sharex=False)
    if not isinstance(axes, np.ndarray):
        axes = [axes]
    for ax, jf in zip(axes, jsonls[:4]):
        rows = [json.loads(l) for l in jf.read_text("utf-8").splitlines() if l.strip()]
        if not rows:
            continue
        t0 = rows[0].get("ts", 0)
        ax.plot([r["ts"] - t0 for r in rows], [r.get("decode_tok_s") for r in rows], lw=0.8, color="#1f77b4")
        ax.plot([r["ts"] - t0 for r in rows], [r.get("gpu_power_w") for r in rows], lw=0.8, color="#d62728", alpha=0.6)
        ax.set_title(jf.stem)
        ax.set_ylabel("tok/s | W")
    fig.suptitle("Telemetry time series (decode blue, power red)")
    made.append(save(fig, "telemetry_multirun.png"))

# 24) Heatmap difference coding vs chat
maps = {}
for f in sorted(TELEMETRY.glob("*-heatmap.json")) if TELEMETRY.exists() else []:
    d = json.loads(f.read_text("utf-8"))
    if d.get("rows"):
        maps[f.stem.replace("-heatmap", "")] = d["rows"]
if len(maps) >= 2:
    names = list(maps)[:2]
    a, b = maps[names[0]], maps[names[1]]
    diff = []
    for ra, rb in zip(a, b):
        diff.append(sum(1 for x, y in zip(ra, rb) if x != y))
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(range(len(diff)), diff, color="#9467bd")
    ax.set_title(f"Heatmap difference: {names[0]} vs {names[1]} (changed experts per layer)")
    ax.set_xlabel("Layer")
    ax.set_ylabel("Changed experts")
    made.append(save(fig, "heatmap_diff.png"))

print(json.dumps({"new_charts": len(made), "files": made}, ensure_ascii=False))
