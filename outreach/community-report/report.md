# Community speed report — Strata-HotRod, Qwen3.8-Flash-Next IQ3_S, RTX 3090

Measured on 2026-11-23/24 with `tools/strata_bench.py` plus a custom 120-run
matrix. Speeds are the engine's own timings; TTFT is client-side over HTTP.

## Hardware and software

- GPU: NVIDIA GeForce RTX 3090, 24 GiB, driver 591.74, WDDM, PCIe 4.0 x16
- CPU: AMD Ryzen 7 5800X (8C/16T); RAM: 95.9 GiB DDR4-2933
- OS: Windows 10 Pro 19045; CUDA 13.1
- Strata-HotRod `ac1ade5f`, engine 0.1.45
- Model: Qwen3.8-Flash-Next IQ3_S (ISTA-DASLab GSQ-RCO), 131072 context,
  MTP spec 4, KV int8, expert-cache auto

## Settings

Default setup with one change: `--vram-reserve-mib 512` instead of 0.
See `configs/recommended-strata-iq3_s.json` in the published repository.

## Results

| Test | Prompt tokens | Decode tok/s (median, range) | Prompt tok/s | TTFT s |
|---|---:|---:|---:|---:|
| short chat | 46 | 62.4 (53.1–74.0), n=9 | — | 0.50 |
| 4K fresh | 4019 | — | 1877.0 (1723.9–1904.9) | 2.17 |
| 16K fresh | 16058 | — | 2396.3 (2349.7–2414.8) | 6.74 |
| agent session | 15239 | 71.5 (57.8–103.0), n=15 | see below | 2.55 |

Agent session conversation-cache hit rate: 69.6 %.

Custom matrix (n=8, bootstrap 95 % CIs):
- VRAM reserve 512: 82.2 tok/s (highest, p=0.22 vs. others — not significant)
- Prefill 32K: `auto:32768` 2539 tok/s vs. `auto:4096` 1782 tok/s
- Context 128K: 53.7 tok/s decode; 200K: 52.3 tok/s
- Dauerlauf 90 min: 2905 requests, 0 errors, RAM flat

## Notes

- With `--vram-reserve-mib 0` the first request after load took 73.6 s;
  with 512 MiB it took 2.2 s. The engine reported 0 MiB free VRAM at load.
- Windows commit limit had only ~4.2 GiB free at start.
- Monitor telemetry: ~53 % GPU alone, ~45 % CPU experts, 0 % disk reads.
- Needle recall: 9/9 at 32K and 128K.

Report folder prepared locally; PR to `Niko1221/Strata` is **not** sent automatically.
