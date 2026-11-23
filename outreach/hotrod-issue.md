# Entwurf für ein Issue in sangharshadhyeta/Strata-HotRod

Titel: Windows/WDDM: `--vram-reserve-mib 0` verursacht ~74 s Stall beim ersten Request

## Beschreibung

Mit der Setup-Default-Konfiguration (`--vram-reserve-mib 0`) meldet der Engine
nach dem Laden: „0 MiB of VRAM free with everything loaded — LOW: requests may
stall". Auf einer RTX 3090 (24 GB) + 96 GB RAM + Windows 10 dauerte der erste
Chat-Request nach dem Start **73,6 s**. Mit 512 MiB waren es **2,2 s**, mit
700 MiB **2,5 s**. Der Decode-Median war mit 512 MiB am höchsten (82,2 vs.
72–79 tok/s), allerdings nicht signifikant (p=0,22, n=8 je Variante).

## Reproduktion

1. Engine mit dem nativen IQ3_S-Pack und `--vram-reserve-mib 0` starten.
2. Erste Anfrage mit ~80 Prompt-Tokens / 96 Output-Tokens senden, Wandzeit messen.
3. Mit 512 und 700 MiB wiederholen.

## Erwartung

Der erste Request nach dem Laden sollte nicht durch WDDM-Overcommit blockieren.

## Weitere Befunde

- **Lernkurve:** Ab geleerten Lerndaten über 150 Requests keine monotone
  Verbesserung; Decode oszilliert 68–89 tok/s (promptklassenabhängig).
  Look-ahead-Learner meldete vereinzelt „rename failed" beim Speichern.
- **SSD-Pfad:** Trotz 96 GB RAM ~0 % Demand-Reads und 0 % Wartezeit in der
  Decode-Timeline; Engpass ist CPU-Experten (~45 %) + GPU (~53 %).
- **Experten im VRAM:** ~8.000–9.000 von 24.576, 2–5 Swaps/Runde; keine
  Korrelation mit Decode (r=0,03, p=0,76).
- **Telemetrie:** Record via `POST /v1/monitor/timeline` und `/metrics`-Polling
  verursachten keinen messbaren Overhead.

Vollständige Daten, Runner und Telemetrie: Repository-Link aus
`outreach/repochad-message.md`.

**Nicht automatisch gepostet.**
