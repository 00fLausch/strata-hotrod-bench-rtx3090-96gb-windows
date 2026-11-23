# TELEMETRY.md — HotRod-Monitor als Datenquelle

## Datenquelle (verifiziert im Quellcode, kein Screenshot/OCR)

| Zweck | Endpunkt | Rate | Quelle im Code |
|---|---|---|---|
| Live-Werte, Experten, Request-Log, Kontext, Timeline | `GET /metrics` (optional `?requests=all&tl_after=<us>&tl_base=<ns>`) | 1 Hz (Frontend-Poll) | `serve/web/app.js` Z. 156–179; `serve/server.py` `renderMetrics` |
| Record (Decode-Timeline) | `POST /v1/monitor/timeline` mit `{"on": true|false}` | einmal pro Lauf | `serve/web/app.js` Z. 519–530; `serve/server.py` Z. 6288 |
| Modellstatus | `GET /v1/status` | Bedarf | Monitor nutzt `/v1/status` + `/api/requests` |
| Request-Details | `GET /api/requests?id=…` | Bedarf | `serve/web/monitor.js` |

`GET /metrics` liefert u. a.:
- `live`: `state`, `tok_s`, `tok_s_mean`, `prefill_tok_s_mean`, `prompt_read/total`, `generated`, `queued`
- `hardware`: `gpu_util`, `gpu_mem_used/total`, `gpu_temp`, `gpu_power`, `gpu_power_limit`,
  `gpu_pcie_gen/width`, `gpu_pcie_rx_mb/tx_mb`, `cpu`, `ram_used/total`, `disk_read_mb`, `disk_write_mb`
- `engine`: `expert_slots`, `expert_cache_mib`, `vram_free_mib`, `prefill_cap`, `kv`, …
- `residency`: `layers`, `experts`, `resident`, `swaps`, `round`, `quality_swaps`, `rows`
  (ein String pro Layer, 512 Zeichen; 0=not in VRAM, 1=resident idle, 2=resident used, 3=resident hot)
- `conversation_cache`: `requests`, `requests_reused`, `reused_tokens`, `parks`, `restores`, …
- `timeline`: `on`, `data` mit `v`, `base_ns`, `now_us`, `last`, `reset`, `layers`, `reads`, `gaps`
- `requests`: Request-Log (Status, Tokens, Abbruchgrund, Timings), `totals`, `history`

Der Record-Schalter schreibt eine Steuerdatei `strata-timeline-<pid>.ctl`; der Engine
schreibt Decode-Fenster in `strata-timeline-<pid>.json`. Der Server behält 15 s
(`TIMELINE_KEEP_US`), daher werden Fenster mit `tl_after`/`tl_base` in 1-s-Polls
abgeholt. `tl_after = data.last`, `tl_base = data.base_ns`.

## Umsetzung im Runner

`runner/telemetry.py` → `TelemetryRecorder`:
- 1 Hz-Poll von `/metrics` während jedes Messlaufs, JSONL `telemetry/<run_id>.jsonl`
  mit `ts` + `run_id` + allen obigen Feldern (ohne die großen Heatmap-Rohdaten).
- `telemetry/<run_id>-summary.json`: Zeitreihen-Statistiken, Experten am Anfang/Ende,
  Swaps/Runde, Swaps/Token, Conversation-Cache, Timeline-Fenster/-Lücken.
- `telemetry/<run_id>-heatmap.json`: Heatmap-Rohdaten (Layer × Experte) am Laufende.
- `record_timeline: true` ruft vor dem Lauf `POST /v1/monitor/timeline {"on":true}` und
  danach `{"on":false}`; Status wird über `/metrics.timeline.on` verifiziert.

## VRAM-Auffälligkeit

Der Monitor zeigt „VRAM 0,6 / 24 GB" (Prozess-spezifischer NVIDIA-Wert) während
`engine.vram_free_mib = 0` und 8.791 Experten im VRAM. Die beiden Werte messen
**unterschiedliche Dinge**: `hardware.gpu_mem_used` ist der aktuelle Prozessanteil
aus NVML, `expert_cache_mib` + `arena_mib` + KV + Dense-Gewichte sind die tatsächliche
Belegung. Siehe B3/B2 in der Auswertung.

## Overhead

T1 misst `telemetry=false` vs. `telemetry=true` (1 Hz) und `record_timeline=false`
vs. `true`, je n=8, mit Mann-Whitney und Bootstrap-KI. Speed-Läufe laufen ohne Record;
Timeline-Läufe (TL_*) sind separate Zusatzläufe mit n=3.

## Datenschutz

Monitor-URLs, Tailscale-IPs/`*.ts.net` und Hostnamen werden vor der Veröffentlichung
durch `runner/privacy.py` geschwärzt. Keine Screenshots.
