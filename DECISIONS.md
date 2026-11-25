# DECISIONS.md - autonomous decisions with rationale

Rule: uncertainty -> choose the more conservative, reversible option; record it
here; keep going.

| # | Date | Decision | Reason / alternative |
|---|---|---|---|
| D01 | 2026-11-23 | No follow-up questions; all choices made autonomously and documented | Explicit instruction: user unreachable |
| D02 | 2026-11-23 | Benchmark against `127.0.0.1:8080`, not the Tailscale IP `[TAILSCALE-IP]` | Local = lowest variance; private IP must be redacted |
| D03 | 2026-11-23 | Copy the original config to `configs/original-strata-iq3_s.json` and verify SHA-256 before every change | Required by the task; restoreability |
| D04 | 2026-11-23 | Use `strata_speed_probe.py` as a template, but build a custom runner with YAML matrix, resume, bootstrap CIs and try/finally | The probe was n=4 and not significant |
| D05 | 2026-11-23 | No changes to Python Tracker files (`config.json`, `AGENTS.md`); only read them and use its start/stop component | Separate project; task concerns only the benchmark |
| D06 | 2026-11-23 | Do not use the local Strata instance as this agent's own language model | Explicit prohibition; the configured OpenCode provider is used instead |
| D07 | 2026-11-23 | Stop background processes only from the explicit list (browser, ComfyUI, Sunshine, Unreal/LiveCoding as "etc."); keep OpenCode, ChatGPT, MCP helpers, tracker/watcher | OpenCode is this agent; tracker controls the server. See `docs/KILLED_PROCESSES.md` |
| D08 | 2026-11-23 | Change power limit / energy plan / Defender only if possible without admin; otherwise document as "not automatable" | Windows user is not an administrator; original always saved |
| D09 | 2026-11-23 | No file deletions outside `D:\strata-bench\`; redirect TEMP/TMP to `D:\strata-bench\tmp` | C: initially had ~0.2 GB free |
| D10 | 2026-11-23 | Statistics: median + IQR + bootstrap 95% CI (seed 20261123); effect only with non-overlapping CIs or Mann-Whitney p<0.05 | Prevents false significance like the probe |
| D11 | 2026-11-23 | Decode tok/s solely from `predicted_n/predicted_ms`, never from wall time | Explicit requirement |
| D12 | 2026-11-23 | n=8 for P1/P2, n=5 from P3; discard but log warm-up per engine start | Time budget vs statistical power |
| D13 | 2026-11-23 | Randomize variants within blocks (seed 20261123); blocks in priority order | Guards against drift; A2 deliberately ordered (start/middle/end) |
| D14 | 2026-11-23 | Test `--max-context 262144` only if the engine starts reliably; otherwise mark "not possible" | 24 GB VRAM and tight commit limit |
| D15 | 2026-11-23 | No new model downloads; small predictor/profile files only if the docs require them for a test | Explicit prohibition; E1 uses existing learning data |
| D16 | 2026-11-23 | No posts/PRs/issues in external repos; only ready-to-send text files under `outreach/` | Explicit prohibition |
| D17 | 2026-11-23 | Automated and manual privacy check before publication; abort if any match remains | Explicit requirement |
| D18 | 2026-11-23 | User hint "leave the model room in RAM/VRAM" incorporated: B1 sweep covers 0/256/512/700/1024/.../4096 MiB; 512 = user's setting, 700 = engine default per `serve/runconfig.py` | Original `--vram-reserve-mib 0` left 0 MiB free; probe hinted at 2048 but n=4 was not significant |
| D19 | 2026-11-23 | Power-limit changes not automatable: `nvidia-smi -pl` returned "Insufficient Permissions" | H1/H2 documented as "not automatable"; 350 W unchanged |
| D20 | 2026-11-23 | After reboot: start engine and runner as detached processes | Two mini-runs were interrupted by messages; config stayed clean |
| D21 | 2026-11-23 | Telemetry from engine `/v1/status` and `/metrics`, not standalone NVML, if NVML hangs | NVML was blocked after GPU process termination |
| D22 | 2026-11-23 | First mini finding: warm-up 73.6 s at reserve 0 vs 2.2 s at 512 and 2.5 s at 700 | Supports the user's hint; confirmed with n=8 significance testing in B1 |
| D23 | 2026-11-23 | Per user request: no further zero-reserve tests. Global default `--vram-reserve-mib 512`; B1 sweep without 0 | 73.6 s stall plus log warning plus user experience |
| D24 | 2026-11-23 | Deep-merge `spec` in `main()` so the global 512 default is not lost when a test defines its own `args` | Otherwise all variants would silently revert to reserve 0 |
| D25 | 2026-11-23 | Extended instruction implemented: telemetry from `GET /metrics` (1 Hz) and Record via `POST /v1/monitor/timeline` for **all** runs; nine earlier results without telemetry discarded and re-run | New mandatory requirement; runner is resume-capable but old runs were not compliant |
| D26 | 2026-11-23 | No Playwright needed: the front-end Record button calls `POST /v1/monitor/timeline {"on":bool}` directly (verified in code) | Fallback 3 not required; fallback 1 succeeded |
| D27 | 2026-11-23 | Speed runs without timeline Record; separate `TL_*` runs with `record_timeline=true` (n=3); overhead measured in T1 (n=8 per arm) | Prevents recording overhead from biasing tok/s |
| D28 | 2026-11-23 | Added blocks T1, D6, D7, TL and B2 (regression analysis); 120 tests total | New priority list from the extended instruction |
| D29 | 2026-11-23 | Power limit still not changeable (no admin); tokens/joule only at the fixed 350 W using telemetry power values | Same as D19, but with power time series available |
| D30 | 2026-11-24 | Initially marked `F2_mtp_off`/`I2_parity_mtp_off` "not possible" when `--mtp`, `--spec` and `--spec-min-p` were removed together | Engine exited immediately with "native pack needs --spec T >= 2" |
| D31 | 2026-11-24 | Commit author corrected to the `00fLausch` account after GitHub attributed the no-reply address to the older `[USER]` account | Repo owner and publishing account must match |
| D32 | 2026-11-24 | Full report translated to English and expanded to 35 charts on user request | Publication target is the international Strata community and RepoChad |
| D33 | 2026-11-25 | Re-ran the previously failed tests. D30 was too pessimistic: removing **only** `--mtp` while keeping `--spec 4` starts the engine. `F2_mtp_off` and `I2_parity_mtp_off` now complete | Verified in `logs/retry-probe*.log`; decode drops from ~82 to 50.2 tok/s without the draft layer, acceptance 0.36 vs 0.64 |
| D34 | 2026-11-25 | `K4_vision_off` remains "not possible": removing `--vision` (with or without vision config changes) makes the engine exit immediately | Verified in two variants in `retry_probe.py` |
| D35 | 2026-11-25 | `G3_defender` re-run with the runner bug fixed; it now fails cleanly with "no admin rights" instead of crashing | `nvidia-smi -pl` and Add-MpPreference both require elevation |
| D36 | 2026-11-25 | Output parity at temperature 0 is **not bit-identical** between MTP draft on/off (different content hashes) | Draft acceptance changes the sampling path; documented as a measured difference |
