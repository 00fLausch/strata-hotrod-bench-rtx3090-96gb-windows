# RESTORE_REPORT - restoration after all benchmark runs

Last restoration: 2026-11-25 22:31-22:33 (after the retry run for the previously
failed variants).

| Item | Original | State after run | Verified |
|---|---|---|---|
| `strata-iq3_s.json` | SHA-256 `47fd4b8d...3f60f82b55f3e4` | identical | yes, hash comparison |
| Power limit | 350 W | 350 W | yes, `nvidia-smi --query-gpu=power.limit` |
| Energy plan | Balanced `381b4222-f694-41f0-9685-ff5bb260df2e` | identical | yes, `powercfg /getactivescheme` |
| Defender exclusion | none | none | limited: not viewable without admin; `Add-MpPreference` failed (access denied), `Remove-MpPreference` executed |
| Learning data `predictor-905fc7359fc3c491.bin` | SHA-256 `c6fd3d6e...76175c1` | identical | yes, hash comparison against `configs/learning-backup/` |
| `.bench-off` leftovers | none | none | yes, directory checked |
| TEMP/TMP | system default | system default for new processes | yes, runner only set them for its own children |
| Engine | running before the run | restarted, `loaded=true` | yes, `/health` |
| Record state (timeline) | off | off | yes, `POST /v1/monitor/timeline {"on":false}` |

**Note on the automatic report:** the "Hash ABWEICHEND" message in
`RESTORE_REPORT.json` was an artifact: the final restore ran without
`--clear_learning`, so it had no expected hash and falsely reported a mismatch.
The direct hash comparison with the real backup confirms correct restoration.

**Note on `power_limit_restored: false`:** `nvidia-smi -pl 350` returned
"Insufficient Permissions" (no admin). The limit was never changed from its
original 350 W, so the system is in the original state.

**Not automatable (manual):** HAGS, cold boot after reboot, RAM 2933 vs 3200 MHz
(XMP, three modules), CUDA Sysmem Fallback Policy, power-limit curve, checking
Defender exclusions (admin required).
