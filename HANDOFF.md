# HANDOFF — nach Neustart / Sitzungsende

## Warum ein Neustart sinnvoll ist
`nvidia-smi` und `pynvml` hängen seit dem Beenden der GPU-Hintergrundprozesse
(UnrealEditor, ComfyUI, Opera) unter WDDM. Der Engine selbst und seine `/metrics`/
`/v1/status`-Telemetrie funktionieren, aber Power-Limit-Änderungen (Block H1) und
NVML-basierte Messungen sind blockiert. Ein sauberer Reboot stellt NVML wieder her.

## Zustand beim Abbruch (verifiziert 2026-11-23 ~14:52)
- `strata-iq3_s.json`: SHA-256 `47FD4B8DAB44B26B6535948C94EC88205DFDE90A26E4A9451A3F60F82B55F3E4` — **identisch mit Original**
- Engine: `http://127.0.0.1:8080/health` → `loaded: true`
- Kein `bench.py`-Prozess aktiv, keine Ergebnisse in `results/`
- Runner-Log: nur „=== Runner gestartet ===" (Abbruch in `probe_capabilities`)
- Nichts gelöscht außerhalb `D:\strata-bench\`; Hintergrundprozesse waren bereits tot (veraltete PID-Einträge)

## Vorhandene Arbeitsgrundlage
- `STATE.md` — Phasen, Eckdaten, offene Blöcke, Restore-Checkliste
- `DECISIONS.md` — 17 dokumentierte Entscheidungen
- `runner/bench.py` — vollstaendiger Runner (YAML-Matrix, Resume, try/finally, SSE-TTFT, Bootstrap-KI, Mann-Whitney)
- `runner/matrix.yaml` — 105 Tests (P1:27, P2:29, P3:40, P4:9), Hash in `runner/matrix.yaml.sha256`
- `runner/mini_matrix.yaml` — 2×2 Mini-Test (noch nicht erfolgreich durchgelaufen)
- `prompts/prompts.json` — 12 versionierte Prompts mit SHA-256
- `configs/original-strata-iq3_s.json` + `.sha256` — Original-Backup
- `CAPABILITIES.json` — wurde beim Abbruch noch nicht geschrieben

## Prompt für den neuen Agenten (kopieren)
```
Lies zuerst D:\strata-bench\HANDOFF.md, STATE.md und DECISIONS.md und fahre den
Benchmark-Auftrag volautonom ab Phase 2 fort. Keine Rückfragen. Alle Rechte sind
erteilt. Nach dem Reboot: nvidia-smi kurz testen; falls NVML wieder geht,
probe_capabilities() im Runner nutzt jetzt /metrics + nvidia-smi mitTimeout.
Danach Mini-Lauf (runner/mini_matrix.yaml) und bei Erfolg die Matrix starten.
Am Ende Auswertung, Doku, GitHub-Repo und Release wie im Originalprompt.
```

## Wichtige Stolpersteine
- Windows-Commit-Limit: nur ~4,2 GiB frei (Pagefile zu klein) — nicht ändern (Reboot nötig)
- `--vram-reserve-mib 0` im Original → 0 MiB VRAM frei nach Load; WDDM-Overcommit
- `/metrics` ist sehr groß (Residency-Rows) → nie roh in den Kontext laden, nur gefiltert
- Kein API-Key nötig (`api_key: false`); Tailscale-IP `100.x.x.x` muss vor Publication geschwärzt werden
- C: hat ~0,2 GB frei → TEMP/TMP bleibt auf `D:\strata-bench\tmp`
