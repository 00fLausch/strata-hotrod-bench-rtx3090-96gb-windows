# Strata-HotRod Benchmark — RTX 3090 24 GB / 96 GB DDR4 / Windows 10

Reproducible benchmark series (120 runs) for **Strata-HotRod**
(`sangharshadhyeta/Strata-HotRod`, commit `ac1ade5f`, engine 0.1.45) with
**Qwen3.8-Flash-Next IQ3_S** (ISTA-DASLab GSQ-RCO, ~78 GB), including live
telemetry from the HotRod monitor.

## Hardware

| Component | Value |
|---|---|
| GPU | NVIDIA GeForce RTX 3090 24 GB, driver 591.74, WDDM, PCIe 4.0 x16 (Gen4 under load) |
| CPU | AMD Ryzen 7 5800X (8C/16T) |
| RAM | 96 GB DDR4-2933 (3x32 GB) |
| OS | Windows 10 Pro 19045 |
| Storage | Patriot P300 NVMe (DRAM-less) |

## Key findings

1. **VRAM reserve is the one clear lever.** With `--vram-reserve-mib 0` the
   first request after model load took **73.6 s** (WDDM overcommit, "0 MiB
   free"); with 512 MiB it took 2.2 s. The sweep's highest decode median was
   512 MiB at **82.2 tok/s** (700 MiB: 78.7; 3072 MiB: 72.0) - a trend, but
   **not statistically significant** (p=0.22).
2. **Prefill chunk size matters at 32K.** `auto:32768` reached 2,539 tok/s and
   TTFT 11.8 s, vs 1,782 tok/s and 16.8 s for `auto:4096`. At 128K the picture
   is mixed (1,665-2,197 tok/s).
3. **Context costs decode.** 4K/16K about 87-93 tok/s, 64K 71 tok/s,
   128K/200K about 52-54 tok/s. Prefill stays around 1,700-2,450 tok/s.
4. **The bottleneck is GPU + CPU experts, not the SSD.** Decode timeline:
   ~53% "GPU alone / host waiting", ~45% CPU experts, **0%** demand reads and
   0% time waiting on in-flight reads. A 90-minute soak produced 2,905
   requests with zero errors, flat RAM at 69.6% and a slight drift from 86 to
   80 tok/s.
5. **Telemetry is free.** Recorder on/off 82.3 vs 77.8 tok/s; Record on/off
   80.7 vs 78.6 tok/s - neither significant. Needle recall at 32K and 128K:
   **9/9 found**.

Standard protocol (`strata bench run`): chat 62.4 tok/s, 4K prefill 1,877
tok/s, 16K prefill 2,396 tok/s, agent session 71.5 tok/s, cache hit rate 69.6%.

## Charts

![Reserve sweep](charts/b1_reserve_decode.png)
![Reserve vs TTFT](charts/b1_reserve_ttft.png)
![Reserve vs expert slots](charts/b1_reserve_experts.png)
![Reserve vs swaps](charts/b1_reserve_swaps.png)
![Context sweep](charts/d1_context_decode.png)
![Context vs prefill](charts/d1_context_prefill.png)
![Context vs TTFT](charts/d1_context_ttft.png)
![Prompt length vs prefill](charts/d7_prompt_prefill.png)
![Prompt length vs TTFT](charts/d7_prompt_ttft.png)
![Decode distribution](charts/decode_distribution.png)
![Decode vs TTFT](charts/decode_vs_ttft.png)
![Experts vs decode](charts/b2_experts_decode.png)
![Experts vs TTFT](charts/experts_vs_ttft.png)
![Swaps per round vs decode](charts/swaps_vs_decode.png)
![Swaps per token vs decode](charts/swaps_per_token_decode.png)
![GPU power vs decode](charts/power_vs_decode.png)
![GPU temperature vs decode](charts/temp_vs_decode.png)
![HotRod switch effects](charts/f1_switch_effects.png)
![MTP acceptance](charts/f2_acceptance.png)
![KV variants](charts/d3_kv_variants.png)
![Long outputs](charts/d4_output_decode.png)
![Conversation cache](charts/d6_convcache.png)
![Reasoning effort](charts/f3_reasoning.png)
![Standard benchmark](charts/a1_standard_bench.png)
![Needle recall](charts/i1_needle_recall.png)
![90-minute soak](charts/j2_soak_trend.png)
![Telemetry time series](charts/telemetry_multirun.png)
![Multi-run telemetry](charts/telemetry_timeseries.png)
![Heatmap difference](charts/heatmap_diff.png)
![Bottleneck analysis](charts/bottleneck.png)
![Timeline gaps](charts/timeline_gaps.png)
![Noise drift](charts/a2_noise.png)
![Learning curve](charts/e1_learning.png)

Interactive overview: [`dashboard/index.html`](dashboard/index.html)

## Recommended configuration

[`configs/recommended-strata-iq3_s.json`](configs/recommended-strata-iq3_s.json)
changes exactly one value: `--vram-reserve-mib 512` instead of 0. Diff and
interpretation: [`docs/RECOMMENDED_DIFF.md`](docs/RECOMMENDED_DIFF.md). The
active configuration on the machine was **not** overwritten.

- **Proven:** reserve 0 causes a first-request stall; needle recall; no SSD
  usage; no measurable telemetry overhead; MTP is mandatory (native pack
  requires `--spec >= 2`).
- **Trend:** 512 MiB slightly faster than 700/2048/3072; chunk 32768 faster at
  32K; slight decline over 90 minutes.
- **No measurable effect:** all individual F1 switches, RAM limits,
  resident-expert count vs decode (r=0.03, p=0.76).
- **Strong effect, now measured:** disabling only the MTP draft layer (keeping
  `--spec 4`) drops decode from about 82 to **50.2 tok/s** and acceptance from
  0.64 to **0.36**. Outputs at temperature 0 are not bit-identical between the
  two modes. The earlier "MTP off not possible" note was wrong and has been
  corrected; removing `--spec` as well is what breaks the engine.

## Methodology

- Fixed hashed prompts: [`prompts/prompts.json`](prompts/prompts.json), 15 items
- n=8 (P1/P2), n=5 (P3+); warm-up discarded and logged after every engine start
- Decode tok/s **only** from engine timings (`predicted_n/predicted_ms`)
- Median, IQR, bootstrap 95% CI (seed 20261123), Mann-Whitney p<0.05
- Variants randomized within blocks; A2 measures drift (66.6→74.7→73.7 tok/s)
- Telemetry: `GET /metrics` at 1 Hz, Record via `POST /v1/monitor/timeline`
  ([TELEMETRY.md](TELEMETRY.md)); speed runs without Record, timeline in extra
  runs (n=3)

## Limits and skipped tests

One GPU, one quantization, one model. Power-limit changes (H1) and the Defender
test (G3) were impossible without admin rights. `K4_vision_off` remains not
possible: removing `--vision` makes the engine exit immediately. Manual only:
HAGS, cold boot, XMP/RAM clock, CUDA Sysmem Fallback Policy. All other tests,
including the two MTP-off variants, were completed.

## Reproduction

```powershell
uv venv .venv --python 3.11
uv pip install --python .venv/Scripts/python.exe numpy pandas matplotlib scipy psutil pynvml pyyaml requests plotly
python runner/make_prompts.py
python runner/make_matrix.py
python runner/bench.py --matrix runner/matrix.yaml
python runner/analyze.py
python runner/charts.py
python runner/more_charts.py
python runner/dashboard.py
python runner/timeline_analysis.py
```

Paths in `runner/bench.py` must be adapted to the local installation (they are
redacted in the published version). See [FLAGS.md](FLAGS.md) for all verified
switches.

## License

MIT - see `LICENSE`.
