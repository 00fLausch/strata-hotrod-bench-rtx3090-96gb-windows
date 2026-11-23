"""Interaktive HTML-Übersicht (plotly) aller Ergebnisse + Telemetrie-Zeitreihen."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dashboard"
CSV = ROOT / "results" / "summary.csv"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    if not CSV.exists():
        print("keine summary.csv")
        return 0
    df = pd.read_csv(CSV)
    for c in ("decode_median", "prefill_median", "ttft_median", "reserve_mib",
              "experts_vram_end", "swaps_per_round", "gpu_power_mean"):
        if c in df:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df[df["decode_median"].notna()]

    figs = []
    if not df.empty:
        f = px.scatter(df, x="reserve_mib", y="decode_median", color="block",
                       error_y="decode_ci_hi", hover_data=["id", "ttft_median", "experts_vram_end"],
                       title="Decode tok/s vs. VRAM-Reserve", template="plotly_white")
        figs.append(("reserve", f))
        f = px.scatter(df, x="experts_vram_end", y="decode_median", color="block",
                       title="Experten im VRAM vs. Decode", template="plotly_white")
        figs.append(("experts", f))
        f = px.bar(df.sort_values("decode_median", ascending=False).head(30),
                   x="id", y="decode_median", color="priority",
                   title="Top 30 Läufe nach Decode", template="plotly_white")
        figs.append(("top", f))
        if "ttft_median" in df:
            f = px.scatter(df, x="prefill_median", y="ttft_median", color="block",
                           title="Prefill vs. TTFT", template="plotly_white")
            figs.append(("ttft", f))

    # Telemetrie-Zeitreihen (erster Lauf mit Daten)
    tl_dir = ROOT / "telemetry"
    tls = sorted(tl_dir.glob("*.jsonl")) if tl_dir.exists() else []
    if tls:
        rows = [json.loads(l) for l in tls[0].read_text("utf-8").splitlines() if l.strip()]
        if rows:
            t0 = rows[0].get("ts", 0)
            keys = [("decode_tok_s", "Decode tok/s"), ("gpu_power_w", "Watt"),
                    ("resident_experts", "Experten im VRAM"), ("disk_read_mb", "Disk read MB")]
            fig = make_subplots(rows=len(keys), cols=1, shared_xaxes=True,
                                subplot_titles=[k[1] for k in keys])
            for i, (k, label) in enumerate(keys, 1):
                fig.add_trace(go.Scatter(x=[r.get("ts", 0) - t0 for r in rows],
                                         y=[r.get(k) for r in rows], name=label), row=i, col=1)
            fig.update_layout(title=f"Telemetrie: {tls[0].stem}", height=700,
                              template="plotly_white")
            figs.append(("telemetry", fig))

    pieces = ["<html><head><meta charset='utf-8'><title>Strata-HotRod Benchmark</title></head><body>",
              "<h1>Strata-HotRod Benchmark — interaktive Übersicht</h1>",
              "<p>Alle Werte aus <code>results/summary.csv</code> und <code>telemetry/*.jsonl</code>.</p>"]
    for name, fig in figs:
        pieces.append(f"<h2>{name}</h2>")
        pieces.append(fig.to_html(full_html=False, include_plotlyjs=("cdn" if name == figs[0][0] else False)))
    pieces.append("</body></html>")
    (OUT / "index.html").write_text("\n".join(pieces), encoding="utf-8")
    print(json.dumps({"dashboard": str(OUT / "index.html"), "charts": len(figs)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
