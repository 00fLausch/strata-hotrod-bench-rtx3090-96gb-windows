# DECISIONS.md — autonome Entscheidungen mit Begründung

Regel: Unsicherheit → konservativere, reversible Option; hier festhalten; weitermachen.

| # | Datum | Entscheidung | Grund / Alternative |
|---|---|---|---|
| D01 | 2026-11-23 | Keine Rückfragen; alle Wahlentscheidungen selbst getroffen und dokumentiert | Expliziter Auftrag: Benutzer nicht erreichbar |
| D02 | 2026-11-23 | Benchmark gegen `127.0.0.1:8080` (lokaler HotRod), nicht gegen Tailscale-IP `[TAILSCALE-IP]` | Lokal = geringste Varianz; Tailscale-IP ist privat und muss geschwärzt werden |
| D03 | 2026-11-23 | Original-Config vor jeder Änderung nach `configs/original-strata-iq3_s.json` kopieren und per SHA-256 verifizieren | Pflicht aus Auftrag; Wiederherstellbarkeit |
| D04 | 2026-11-23 | Probe-Skript `strata_speed_probe.py` als Vorlage, aber eigener Runner mit YAML-Matrix, Resume, Bootstrap-KI und try/finally | Roboteranforderung; Probe war n=4 und nicht signifikant |
| D05 | 2026-11-23 | Keine Änderung an Python-Tracker-Dateien (`config.json`, `AGENTS.md`); nur lesen und ihre Start/Stop-Komponente nutzen | Fremdes Projekt; expliziter Auftrag betrifft nur Benchmark; AGENTS.md verlangt zusätzliche Tests für Änderungen |
| D06 | 2026-11-23 | Die lokal laufende Strata-Instanz NICHT als eigenes Sprachmodell für meine Arbeit verwenden | Explizites Verbot; ich nutze meinen konfigurierten OpenCode-Provider |
| D07 | 2026-11-23 | Hintergrundprozesse nur gemäß expliziter Liste beenden (Browser, ComfyUI, Sunshine, Unreal/LiveCoding als „usw."); OpenCode, ChatGPT, MCP-Helfer, Tracker/Watcher laufen lassen | OpenCode bin ich selbst; Tracker steuert den Server. Liste in `docs/KILLED_PROCESSES.md` |
| D08 | 2026-11-23 | Power-Limit/Energieplan/Defender nur ändern, wenn ohne Admin-Rechte möglich; sonst als „nicht automatisierbar" dokumentieren | Windows-User ist nicht Administrator; Vorher-Test, Original immer sichern |
| D09 | 2026-11-23 | Keine Dateien außerhalb `D:\strata-bench\` löschen; TEMP/TMP auf `D:\strata-bench\tmp` umleiten | C: war initially ~0,2 GB frei (nach Reboot 38,8 GB), Regel bleibt bestehen |
| D10 | 2026-11-23 | Statistik: Median + IQR + Bootstrap-95%-KI (Seed 20261123); Effekt nur bei nicht überlappenden KIs oder Mann-Whitney p<0,05 | Explizite Methodik; verhindert Scheinsignifikanz wie bei der Probe |
| D11 | 2026-11-23 | Decode tok/s ausschließlich aus `predicted_n/predicted_ms` (Engine-Timings), nie aus Wandzeit | Explizite Vorgabe |
| D12 | 2026-11-23 | n=8 für P1/P2, n=5 ab P3; Warm-up pro Start verwerfen, aber loggen | Zeitbudget vs. statistische Güte |
| D13 | 2026-11-23 | Varianten innerhalb eines Blocks randomisieren (Seed 20261123), Blöcke in Prioritätsreihenfolge | Gegen Drift durch Temperatur/Lernen/Cache; A2 absichtlich geordnet (Start/Mitte/Ende) |
| D14 | 2026-11-23 | `--max-context 262144` (D1/D2) nur testen, wenn Engine stabil startet; sonst „nicht möglich" | 24 GB VRAM + knappes Commit-Limit; Fail → Retry → dokumentieren |
| D15 | 2026-11-23 | Keine neuen Modelle herunterladen; kleine Predictor-/Profil-Dateien nur wenn Doku es für einen Test vorsieht | Explizites Verbot; E1 nutzt vorhandene Lerndaten |
| D16 | 2026-11-23 | Keine Posts/PRs/Issues in fremden Repos; nur fertige Texte unter `outreach/` | Explizites Verbot |
| D17 | 2026-11-23 | Vor Publication automatisierte + manuelle Datenschutzprüfung; bei Treffer → nicht veröffentlichen | Explizite Pflicht |
| D18 | 2026-11-23 | Nutzerhinweis „dem Modell Platz im RAM/VRAM lassen" aufgenommen: B1-Sweep um **0 / 256 / 512 / 700 / 1024 / … / 4096 MiB** erweitert; 512 = bewährte Nutzer-Einstellung, 700 = Engine-Default laut `serve/runconfig.py` | Original `--vram-reserve-mib 0` → 0 MiB frei, Log warnt vor Stalls; Probe zeigt Tendenz zugunsten 2048, aber n=4 nicht signifikant |
| D19 | 2026-11-23 | Power-Limit-Änderung nicht automatisierbar: `nvidia-smi -pl` → „Insufficient Permissions" (kein Admin) | H1/H2 werden als „nicht automatisierbar, manuell möglich" dokumentiert; Original 350 W bleibt unverändert |
| D20 | 2026-11-23 | Nach Reboot: Engine und Runner als **detachte** Prozesse starten (Start-Process), damit Interaktionen den Lauf nicht abbrechen | Zwei Mini-Läufe wurden durch Nachrichten unterbrochen; Config war beide Male sauber |
| D21 | 2026-11-23 | H1/H2/H3-Telemetrie aus Engine-`/v1/status` und `/metrics`, nicht aus NVML, falls NVML erneut hängt | NVML war nach GPU-Prozess-Beendigung blockiert; Engine-Timings sind ohnehin die Messgröße |
| D22 | 2026-11-23 | Erster Mini-Befund: Warm-up bei Reserve 0 = **73,6 s**, bei 512 = 2,2 s, bei 700 = 2,5 s | Stützt Nutzerhinweis; wird durch B1 mit n=8 und Signifikanzprüfung abgesichert, nicht als Einzelmessung überinterpretiert |
| D23 | 2026-11-23 | Auf Nutzerwunsch: **keine weiteren Nullreserve-Tests**. Globaler Default `--vram-reserve-mib 512` für alle Tests; B1-Sweep ohne 0; bereits gemessene 0er-Werte bleiben als historischer Befund dokumentiert | 73,6 s Stall + Log-Warnung + Nutzer-Erfahrung; 512 ist die bewährte Einstellung |
| D24 | 2026-11-23 | `spec` wird in `main()` tief zusammengeführt, damit der globale 512er-Default nicht durch Test-spezifische `args` verloren geht | Sonst hätten alle Varianten stillschweigend wieder Reserve 0 benutzt |
| D25 | 2026-11-23 | Erweiterte Vorgabe umgesetzt: Telemetrie aus `GET /metrics` (1 Hz) und Record via `POST /v1/monitor/timeline` für **alle** Messläufe; vorherige 9 Ergebnisse ohne Telemetrie verworfen und neu gestartet | Neue Pflichtvorgabe; Runner ist resume-fähig, aber alte Läufe waren nicht konform |
| D26 | 2026-11-23 | Kein Playwright nötig: Record-Button im Frontend ruft direkt `POST /v1/monitor/timeline {"on":bool}`; im Code verifiziert | Fallback 3 der Vorgabe entfällt; Fallback 1 erfolgreich |
| D27 | 2026-11-23 | Speed-Läufe ohne Timeline-Record; eigene `TL_*`-Läufe mit `record_timeline=true` (n=3); Overhead separat in T1 (n=8 je Arm) | Verhindert Verfälschung der tok/s durch Recording |
| D28 | 2026-11-23 | Neue Blöcke T1, D6, D7, TL und B2 (Regressionsauswertung) in Matrix ergänzt; insgesamt 120 Tests | Neue Prioritätenliste der Vorgabe |
| D29 | 2026-11-23 | Power-Limit weiterhin nicht änderbar (kein Admin) → H1/Tokens-pro-Joule nur mit Telemetrie-Leistungswerten bei 350 W, keine Kurve | Wie D19; diesmal aber Watt-Zeitreihen aus `/metrics` vorhanden |
