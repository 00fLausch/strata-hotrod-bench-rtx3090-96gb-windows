# STATE.md - benchmark run state

Last update: 2026-11-24 (all phases complete)
Session: `ses_df76b397effd7bOGECT3ZOLyPO`
Agent: fully autonomous, no follow-up questions; decisions in `DECISIONS.md`.

## Time budget

- Start: 2026-11-23 ~14:20 local
- Measurement end: 2026-11-23 23:59
- Publication: 2026-11-24
- 14-hour budget respected.

## Phases

| Phase | Status | Note |
|---|---|---|
| 1 Exploration | done | repo/config/probe/API/flags/GPU/monitor endpoints recorded |
| 2 Preparation | done | venv, runner, telemetry recorder, prompts, mini-run |
| 3 Measurements | done | 120 tests, priority 1-4 |
| 4 Restore | done | config, power, plan, learning data, engine - see `RESTORE_REPORT.md` |
| 5 Analysis | done | tables, 35 charts, Plotly dashboard, bottleneck analysis |
| 6 Publication | done | public repo + release v1.0 |

## Verified system facts

- HotRod repo: `[DRIVE]/Users/[USER]\Desktop\python.toolz\apps\strata`,
  remote `sangharshadhyeta/Strata-HotRod`, HEAD `ac1ade5f22f7f0bbaf654d9a24c0ccaf040950ea`
- Engine: `engine\strata.exe` version 0.1.45, API `http://127.0.0.1:8080`
- Model: IQ3_S (2 GGUF + PLE shard), pack `D:\Strata-HotRod-data\packs\iq3_s`
- Baseline config: `configs/original-strata-iq3_s.json` (SHA-256 `47fd4b8d...`)
- Recommended config: `configs/recommended-strata-iq3_s.json` (reserve 512)
- GPU: RTX 3090 24 GB, driver 591.74, power limit 350 W, PCIe 4.0 x16 under load
- Standard protocol result: chat 62.4 tok/s, 4K prefill 1877 tok/s, 16K 2396 tok/s
- Key finding: reserve 0 -> 73.6 s warm-up stall; 512 -> 2.2 s

## Results

- `results/summary.csv`, `results/statistics.json`, `docs/RESULTS_TABLES.md`
- `telemetry/*.jsonl` + summaries + raw timelines + heatmaps
- `charts/*.png` (35), `dashboard/index.html`
- `results/bottleneck.json` (~53% GPU alone, ~45% CPU experts, 0% disk)

## Publication

- Repository: `https://github.com/00fLausch/strata-hotrod-bench-rtx3090-96gb-windows`
- Release: v1.0 with results zip
- Contributor attribution corrected to the `00fLausch` account

## Restore checklist

- [x] Original config restored and verified
- [x] Power limit 350 W verified
- [x] Energy plan restored and verified
- [x] Defender exclusion removed (not viewable without admin)
- [x] Learning data restored and hash-verified
- [x] Engine restarted, `loaded=true`
- [x] TEMP/TMP of started processes reset
- [x] Record state off
