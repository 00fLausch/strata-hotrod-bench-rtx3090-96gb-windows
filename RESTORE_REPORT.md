# RESTORE_REPORT — Wiederherstellung nach dem Benchmark-Lauf

Zeitpunkt: 2026-11-23 23:57–23:59

| Element | Original | Zustand nach Lauf | Verifiziert |
|---|---|---|---|
| `strata-iq3_s.json` | SHA-256 `47fd4b8d…3f60f82b55f3e4` | identisch | ✅ Hash-Vergleich |
| Power-Limit | 350 W | 350 W | ✅ `nvidia-smi --query-gpu=power.limit` |
| Energieplan | Ausbalanciert `381b4222-f694-41f0-9685-ff5bb260df2e` | identisch | ✅ `powercfg /getactivescheme` |
| Defender-Ausnahme | keine gesetzt | keine gesetzt | ⚠️ Nicht ohne Admin einsehbar; `Add-MpPreference` schlug fehl (Zugriff verweigert), `Remove-MpPreference` wurde ausgeführt |
| Lerndaten `predictor-905fc7359fc3c491.bin` | SHA-256 `c6fd3d6e…76175c1` | identisch | ✅ Hash-Vergleich mit `configs/learning-backup/` |
| `.bench-off`-Reste | keine | keine | ✅ Verzeichnis geprüft |
| TEMP/TMP | System-Default | System-Default (neue Prozesse) | ✅ Runner setzte nur eigene Kindprozesse um |
| Engine | lief vor dem Lauf | neu gestartet, `loaded=true` | ✅ `/health` |
| Record-Status (Timeline) | aus | aus | ✅ `POST /v1/monitor/timeline {"on":false}` |

**Hinweis zum automatischen Report:** Die Meldung „Hash ABWEICHEND" im
`RESTORE_REPORT.json` war ein Artefakt: Der finale Restore lief ohne
`--clear_learning`, daher hatte er keinen erwarteten Hash und meldete fälschlich
eine Abweichung. Der direkte Hash-Vergleich mit dem echten Backup (siehe oben)
bestätigt die korrekte Wiederherstellung.

**Nicht automatisierbar (manuell möglich):** HAGS, Kaltstart nach Reboot,
RAM 2933 vs. 3200 MHz (XMP, 3 Module), CUDA Sysmem Fallback Policy,
Power-Limit-Kurve, Defender-Ausnahme prüfen (Admin nötig).
