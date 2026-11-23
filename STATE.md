# STATE.md — Strata-HotRod Benchmark (autonomer Lauf)

Letztes Update: 2026-11-23 (Phase 1/2)
Session: `ses_df76b397effd7bOGECT3ZOLyPO`
Agent: vollautonom, keine Rückfragen, Entscheidungen in `DECISIONS.md`.

## Zeitbudget
- Start: 2026-11-23 ~14:20 lokal
- Limit: 14 h → Ende spätestens 2026-11-24 ~04:20
- Reserviert für Auswertung/Doku/Publikation: mind. 1,5 h (ab ~02:50)

## Phasen
| Phase | Status | Notiz |
|---|---|---|
| 1 Erkundung | ✅ erledigt | Repo/Config/Probe/API/Flags/GPU erfasst |
| 2 Vorbereitung | 🔄 laufend | venv, Runner, Prompts, Mini-Lauf |
| 3 Messungen | ⬜ offen | P1 → P2 → P3 → P4 |
| 4 Aufräumen/Wiederherstellen | ⬜ offen | try/finally im Runner + RESTORE_REPORT.md |
| 5 Auswertung | ⬜ offen | Tabellen, Diagramme, Empfehlung |
| 6 Veröffentlichung | ✅ erledigt | Repo, Release, Outreach-Texte |

## Erkundung — gesicherte Eckdaten
- **HotRod-Repo:** `C:\Users\flauschbert\Desktop\python.toolz\apps\strata`, remote `sangharshadhyeta/Strata-HotRod`, HEAD `ac1ade5f22f7f0bbaf654d9a24c0ccaf040950ea` (2026-11-15)
- **Offizielle Strata-App:** `C:\Users\flauschbert\AppData\Local\Programs\Strata` (A3: evtl. nicht dasselbe → prüfen)
- **Engine:** `engine\strata.exe`, Version `0.1.45`, `--serve`, API `http://127.0.0.1:8080`
- **Modell:** IQ3_S (2 GGUFs + PLE-Shard) auf `D:\Strata-HotRod-data\models\IQ3_S`, Pack `D:\Strata-HotRod-data\packs\iq3_s`, MTP `D:\Strata-HotRod-data\mtp\rt`
- **Probe:** `...\python-tracker\artifacts\strata-speed-probe-20261123\probe.json` + `strata_speed_probe.py` (als Runner-Vorlage übernommen)
- **Aktive Config:** `...\apps\strata\strata-iq3_s.json` — Original gesichert unter `configs/original-strata-iq3_s.json`
- **Steuerung:** Tracker-`.venv\python.exe -m serve.server --config ... --port 8080`; Stop via `python-tracker\strata_control.py --config ...`
- **API-Key:** nicht nötig (`/health` → `api_key: false`) — kein Schlüssel in Artefakte schreiben
- **Metriken:** `/v1/status` (letzte Timings), `/metrics` (JSON: engine/live/requests/hardware) — `/metrics` ist sehr groß, nur gefiltert verarbeiten
- **Antwort-Timings:** `prompt_n/prompt_ms/prompt_per_second`, `predicted_n/predicted_ms/predicted_per_second`, `draft_n/draft_n_accepted`, `cache_n`
- **GPU:** RTX 3090 24 GB, Treiber 591.74, Power-Limit 350 W (Min 100, Max 350), PCIe Gen1×16 im Leerlauf (unter Last prüfen), Ryzen 7 5800X, 96 GB DDR4
- **Befund Probe:** Decode-Medians 66–73 tok/s, n=4, Streuung 60–87 → nicht signifikant. Reserve 512 → 3 Shrinks, Reserve 2048 → 2 Shrinks.
- **Warnung Log:** Windows-Commit-Limit 131,8 GiB, nur 4,2 GiB frei; 0 MiB VRAM frei nach Load (WDDM-Overcommit). `--vram-reserve-mib 0` im Original.

## Offene Blöcke (Priorität)
- P1: A1, A2, B1, B2, C1, D1
- P2: E1, E3, E4, F1, F2, G1, G2, I1
- P3: B3, B6, C2, C3, D2, D3, D4, D5, E5, F3, F4, F5, H1, I2, I3
- P4: A3, G3, G4, H2, H4, I4, J1, J2, J3, K

## Wiederherstellungs-Checkliste
- [ ] Config-Original zurückgesetzt + verifiziert (Hash)
- [ ] Power-Limit 350 W + verifiziert
- [ ] Energieplan original + verifiziert
- [ ] Defender-Ausnahme entfernt + verifiziert
- [ ] Lerndaten (predictor/profile/standin) zurückgespielt + verifiziert
- [ ] Engine neu gestartet und `/health loaded=true`
- [ ] TEMP/TMP der gestarteten Prozesse wieder original

## Bei Unterbrechung
Dieses Dokument + `DECISIONS.md` + `results/*.json` sind die einzige Grundlage.
Runner ist resume-fähig: vorhandene abgeschlossene `results/<test_id>.json` werden übersprungen.
