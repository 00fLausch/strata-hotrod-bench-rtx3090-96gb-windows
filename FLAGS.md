# FLAGS.md — tatsächlich existierende Performance-Flags / Env-Variablen

Quellen: `engine\strata.exe --help` (vollständig gespeichert in `docs/engine-help.txt`),
`serve/runconfig.py`, aktive `strata-iq3_s.json`, `docs/FEATURES-qwen.md`, `docs/HOTROD-DETAILS.md`.
Nur Flags mit dokumentierter Wirkung auf Speed/Speicher sind gelistet. „Default" = Engine-Default,
nicht zwingend Wert der aktiven Config.

## VRAM / Cache

| Flag | Default | Wirkung |
|---|---|---|
| `--vram-reserve-mib N` | 700 MiB | VRAM, das für andere Programme freigehalten wird. Aktive Config: **0** (→ 0 MiB frei nach Load, Warnung vor Stalls). Nutzer-Einstellung: 512. |
| `--vram-elastic` | aus | Expert-Cache in Segmenten (512 MiB); erlaubt `POST /v1/vram` und Vision-Elastic. Aktiv in Config. |
| `--expert-cache N\|auto` | 0 | Experten-Blobs in VRAM, GPU-Computation. |
| `--expert-cache-per-layer` | aus | Eigene Slots pro Layer statt gemeinsamem Zähler. |
| `--kv fp16\|int8\|q4_0\|k8v4` | fp16 | KV-Speicherform. Aktiv: int8. |
| `--kv-resident N` | 0 | N KV-Zellen in VRAM, Rest in gepinntem RAM. Aktiv: 32768. |
| `--kv-grow` | aus | KV nimmt nur erreichte Zellen in VRAM. |
| `--prefill CHUNK\|auto[:N]` | auto | Batched Prompt-Verarbeitung; `auto:16384/32768` erlaubt größere Chunks. Aktiv: auto:16384. |
| `--prefill-head-alias` | aus | Output-Head während Prefill entladen. |
| `--prompt-cache N` | 6 | Checkpoints zwischen Requests. |
| `--prompt-cache-every N` | 16384 | Checkpoint alle N frischen Prompt-Tokens. |
| `--prompt-cache-tail` | aus | Extra Checkpoint nahe Prompt-Ende. |
| `--prompt-cache-spread` | aus | Checkpoints nach hinten verteilt. |
| `--conversation-cache-mib N` | 0 | RAM-Budget für geparkte Konversationen. |
| `--memory-limit-mib N` | 0 | RAM-Limit des Engines (für G2). |

## MTP / Speculative Decoding

| Flag | Default | Wirkung |
|---|---|---|
| `--spec N` | – | Verify-Fenster des Draft-Layers. Aktiv: 4. |
| `--spec-min-p P` | – | Schwelle für zusätzliche Draft-Guesses. Aktiv: 0.5. |
| `--mtp DIR` | – | Draft-Layer-Pfad. Aktiv: `D:\Strata-HotRod-data\mtp\rt`. |
| `--suffix-draft N` | 3 | Prompt-Lookup-Drafts. |
| `--lookup-chain K` | 0 | Zusätzliche Prompt-Lookup-Drafts. |
| `--spec-prob-accept` / `--no-spec-prob-accept` | an | Probabilistische Draft-Akzeptanz. |
| `--coupled-draft` / `--no-coupled-draft` | an | Coupled Draft Sampling. |
| `--mtp-q4 all\|proj\|head` | aus | 4-Bit Draft-Projektionen/Head. |

## Experten / Routing (HotRod-spezifisch)

| Flag | Default | Wirkung |
|---|---|---|
| `--expert-profile P` | – | VRAM-Tier aus Profil vorladen. Aktiv: `data\expert-profile.bin`. |
| `--expert-profile-save P` | aus | Gelernte Expertise als Profil speichern. |
| `--adapt-min-gain F` | 1.5 | Swap-Schwelle des adaptiven Tiers. |
| `--adapt-async 1` | 0 | Swaps zwischen Verify-Windows (nicht bitgleich). |
| `--no-hit-poke` | aus | A/B: Treiber-Poke nach Hit-Launch aus. |
| `--no-ple-prefetch` | aus | A/B: PLE-Zeilen einzeln statt PrefetchVirtualMemory. |
| `--no-pool` | aus | CPU-Expert-Pool aus (GPU-only-Floor). |
| `--pool-workers N` | 0 (= alle physischen Kerne minus 1) | Anzahl Pool-Worker. |
| `--pool-tasks N` | 0 | Batched CPU-Tasks pro Phase. |
| `--host-core first\|last\|sibling` | first | Host-Thread-Core (GPU-Interrupts). |
| `--aux-cpus off\|auto\|LIST` | off | Platzierung der restlichen Threads. |
| `--pool-affinity all\|auto\|p-cores` | all | Worker-Affinität. |
| `--mmap-experts` | aus | A/B: zurück zu MapViewOfFile statt Resident-Arena. |
| `--resident-experts` | aus | Low-RAM-Modus (mmap + resident CPU experts). |

## PLE / SSD

| Flag | Default | Wirkung |
|---|---|---|
| `--ple-io direct\|mmap\|ram` | direct | SSD-Zeilen lesen / gemappt / komplett in RAM. |
| `--ple-row-cache N` | 1048576 | Zeilen-Cache (90 B pro Zeile). |
| `--ple-inflight N` | 256 | Ausstehende SSD-Reads. |
| `--no-ple` | aus | PLE-Layer komplett aus (diagnostisch). |

## Kontext / Sampling

| Flag | Default | Wirkung |
|---|---|---|
| `--max-context N` | 4096 | KV/State-Kapazität. Aktiv: 131072. |
| `--rope-scaling none\|linear\|yarn` | Modelldatei | Kontext-Erweiterung. |
| `--temperature F`, `--top-k N`, `--top-p F`, `--seed S` | – | Sampling (request-level überschreibbar). |

## Relevante Env-Variablen (aus aktiver Config)

| Variable | Aktiver Wert | Bedeutung |
|---|---|---|
| `STRATA_HC_Q8` | 1 | Q8_0 Hyperconnection-Verify-Read. |
| `STRATA_ROUTE_TAIL_SKIP` | 0 | Tail-Skip im Router. |
| `STRATA_RESIDENT_HEADROOM_GIB` | 6 | Headroom für resident Experten. |
| `STRATA_ARENA_PIN_GIB` | 40 | Cap für CUDA-Pinning der Arena. |
| `STRATA_KVA` | 1 | KV-Arena. |
| `STRATA_ROUTE_RESIDENT` | 1e30 | Residency-Bias-Marge. |
| `STRATA_ROUTE_RESIDENT_RANKS` | 3-9 | Betroffene Ränge. |
| `STRATA_ROUTE_RESIDENT_EDGE` | 1 | Edge-Experimental. |
| `STRATA_SWAP2_MAX` | 2 | SWAP2-Limit. |
| `STRATA_SWAP2_GAP` | 1 | SWAP2-Gap. |
| `STRATA_KV_GROW_INIT` | 4096 | Initiale KV-Grow-Größe. |
| `STRATA_LA_LEARN` | 1 | Look-ahead-Lernen. |
| `STRATA_MASK` | 0.05 | Experten-Masking (aus Log). |
| `STRATA_PREFILL_CPU_SHARE` | auto | CPU-Anteil am Prefill (nur wenn Commit-Limit reicht). |

## Nicht automatisierbar (dokumentiert, nicht getestet)

- `--gpu-only-full`, `--graph-only`: diagnostische GPU-Floors, keine Server-Messung.
- `--debug`-Flags (`--dump-*`, `--sync-every-layer`, `--check-logits`): verändern Messpfad.
- `--control-vector*`: erlaubt, aber kein Performance-Schalter ohne Modell-Datei.
