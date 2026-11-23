# TELEMETRY.md - HotRod monitor as a data source

## Source (verified in source code, no screenshots/OCR)

| Purpose | Endpoint | Rate | Source in code |
|---|---|---|---|
| Live values, experts, request log, context, timeline | `GET /metrics` (optional `?requests=all&tl_after=<us>&tl_base=<ns>`) | 1 Hz (front-end poll) | `serve/web/app.js` lines 156-179; `serve/server.py` |
| Record (decode timeline) | `POST /v1/monitor/timeline` with `{"on": true\|false}` | once per run | `serve/web/app.js` lines 519-530; `serve/server.py` line 6288 |
| Model status | `GET /v1/status` | on demand | Monitor uses `/v1/status` + `/api/requests` |
| Request details | `GET /api/requests?id=...` | on demand | `serve/web/monitor.js` |

`GET /metrics` provides, among other things:

- `live`: `state`, `tok_s`, `tok_s_mean`, `prefill_tok_s_mean`, `prompt_read/total`,
  `generated`, `queued`
- `hardware`: `gpu_util`, `gpu_mem_used/total`, `gpu_temp`, `gpu_power`,
  `gpu_power_limit`, `gpu_pcie_gen/width`, `gpu_pcie_rx_mb/tx_mb`, `cpu`,
  `ram_used/total`, `disk_read_mb`, `disk_write_mb`
- `engine`: `expert_slots`, `expert_cache_mib`, `vram_free_mib`, `prefill_cap`,
  `kv`, ...
- `residency`: `layers`, `experts`, `resident`, `swaps`, `round`, `quality_swaps`,
  `rows` (one string per layer, 512 characters; 0=not in VRAM, 1=resident idle,
  2=resident used, 3=resident hot)
- `conversation_cache`: `requests`, `requests_reused`, `reused_tokens`, `parks`,
  `restores`, ...
- `timeline`: `on`, `data` with `v`, `base_ns`, `now_us`, `last`, `reset`,
  `layers`, `reads`, `gaps`
- `requests`: request log (state, tokens, stop reason, timings), `totals`, `history`

The Record switch writes a control file `strata-timeline-<pid>.ctl`; the engine
writes decode windows to `strata-timeline-<pid>.json`. The server keeps 15 s
(`TIMELINE_KEEP_US`), so windows are fetched with `tl_after`/`tl_base` in 1 Hz
polls. `tl_after = data.last`, `tl_base = data.base_ns`.

## Runner implementation

`runner/telemetry.py` -> `TelemetryRecorder`:

- 1 Hz polling of `/metrics` during every measurement run; JSONL
  `telemetry/<run_id>.jsonl` with `ts` + `run_id` + all fields above (without
  the large heatmap raw data).
- `telemetry/<run_id>-summary.json`: time-series statistics, experts at
  start/end, swaps per round, swaps per token, conversation cache, timeline
  windows/gaps.
- `telemetry/<run_id>-timeline.json`: raw timeline layers, reads and gaps.
- `telemetry/<run_id>-heatmap.json`: raw heatmap (layer x expert) at run end.
- `record_timeline: true` calls `POST /v1/monitor/timeline {"on":true}` before
  and `{"on":false}` after the run; status is verified via `/metrics.timeline.on`.

## VRAM discrepancy

The monitor shows "VRAM 0.6 / 24 GB" (process-specific NVML value) while
`engine.vram_free_mib = 0` and 8,791 experts are in VRAM. These values measure
**different things**: `hardware.gpu_mem_used` is the current process share from
NVML, whereas `expert_cache_mib` + `arena_mib` + KV + dense weights are the
actual allocation. See blocks B2/B3 in the analysis.

## Overhead

T1 measures `telemetry=false` vs `telemetry=true` (1 Hz) and
`record_timeline=false` vs `true`, n=8 each, with Mann-Whitney and bootstrap
CIs. Speed runs have no Record; `TL_*` runs are separate additional runs with
n=3.

## Privacy

Monitor URLs, Tailscale IPs/`*.ts.net` and host names are redacted before
publication by `runner/privacy.py`. No screenshots are used.
