# Reddit-Entwurf für r/LocalLLaMA (manuell posten)

**Title:** Strata-HotRod + Qwen3.8-Flash-Next IQ3_S on one RTX 3090: 120-run benchmark with live monitor telemetry

**Body:**

I benchmarked my local Strata-HotRod server systematically and published
everything (runner, prompts, raw JSON, telemetry JSONL, charts, interactive
dashboard, recommended config):

https://github.com/00fLausch/strata-hotrod-bench-rtx3090-96gb-windows

Setup: RTX 3090 24 GB, Ryzen 7 5800X, 96 GB DDR4-2933, Windows 10, engine 0.1.45.

Key numbers (n=8, bootstrap 95% CIs):
- Decode 62–82 tok/s depending on config; 4K prefill 1,877 tok/s, 16K 2,396 tok/s
- 32K prefill: chunk 32768 → 2,539 tok/s vs chunk 4096 → 1,782 tok/s
- 128K decode ~54 tok/s, 200K ~52 tok/s, needle recall 9/9 at 32K and 128K
- 90-min soak: 2,905 requests, zero errors, RAM flat at 69.6%

The most practical finding: the stock `--vram-reserve-mib 0` made the first
request after load take 73.6 s; 512 MiB fixed it (2.2 s). Not statistically
significant for steady-state speed, but very noticeable interactively.

Also interesting: the decode timeline shows ~53% GPU-alone and ~45% CPU
experts, with 0% SSD demand reads — this is a CPU-expert-bound setup even
with lots of RAM. Monitor telemetry had no measurable overhead.

Limitations: one GPU, one quant, no power-limit sweep (no admin), Windows
commit limit was tight. Happy to answer questions or add tests.
