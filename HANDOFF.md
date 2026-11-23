# HANDOFF - for a new agent

The run is complete. This file documents the state in case the session is
interrupted before further work.

## What exists

- `STATE.md`: phases, verified facts, restore checklist
- `DECISIONS.md`: 32 autonomous decisions with rationale
- `runner/bench.py`: full runner (YAML matrix, resume, try/finally, SSE TTFT,
  bootstrap CIs, Mann-Whitney, telemetry recorder integration)
- `runner/matrix.yaml`: 120 tests, SHA-256 in `runner/matrix.yaml.sha256`
- `runner/telemetry.py`: HotRod monitor recorder (`/metrics` + Record endpoint)
- `runner/analyze.py`, `charts.py`, `more_charts.py`, `dashboard.py`,
  `timeline_analysis.py`, `privacy.py`, `publish.py`
- `prompts/prompts.json`: 15 hashed prompts
- `configs/original-strata-iq3_s.json`, `configs/recommended-strata-iq3_s.json`
- `telemetry/`, `results/`, `charts/` (35 PNGs), `dashboard/index.html`

## Already published

`https://github.com/00fLausch/strata-hotrod-bench-rtx3090-96gb-windows`
Release v1.0. If anything must be changed: edit in `D:\strata-bench`, copy to
`D:\strata-bench\publish`, commit and push from there. Keep the commit author as
`00fLausch <[EMAIL]>`.

## Known pitfalls

- Windows commit limit was tight (~4.2 GiB free at the start); do not change it.
- `--vram-reserve-mib 0` leaves 0 MiB VRAM free and stalls the first request.
- `/metrics` is large (residency rows); always filter it in scripts, never dump
  it into the agent context.
- No API key needed (`api_key: false`); redact Tailscale IPs and host names.
- MTP cannot be disabled on the native IQ pack (`--spec >= 2` required).
- Power-limit changes and Defender changes require admin rights (not available).
