# FLAGS.md - verified performance flags and environment variables

Sources: `engine\strata.exe --help` (full output in `docs/engine-help.txt`),
`serve/runconfig.py`, active `strata-iq3_s.json`, `docs/FEATURES-qwen.md`,
`docs/HOTROD-DETAILS.md`. Only flags with documented speed/memory impact are
listed. "Default" is the engine default, not necessarily the active config.

## VRAM / cache

| Flag | Default | Effect |
|---|---|---|
| `--vram-reserve-mib N` | 700 MiB | VRAM kept free for other programs. Active config: **0** (0 MiB free after load, stall warning). User setting: 512. |
| `--vram-elastic` | off | Expert cache in segments (512 MiB); enables `POST /v1/vram` and elastic vision. Active. |
| `--expert-cache N\|auto` | 0 | Expert blobs resident in VRAM, computed on GPU. |
| `--expert-cache-per-layer` | off | Separate slots per layer instead of a shared counter. |
| `--kv fp16\|int8\|q4_0\|k8v4` | fp16 | KV storage format. Active: int8. |
| `--kv-resident N` | 0 | N KV cells in VRAM, rest in pinned RAM. Active: 32768. |
| `--kv-grow` | off | KV takes VRAM only for cells actually reached. |
| `--prefill CHUNK\|auto[:N]` | auto | Batched prompt processing; `auto:16384/32768` allow larger chunks. Active: auto:16384. |
| `--prefill-head-alias` | off | Unload output head during prefill. |
| `--prompt-cache N` | 6 | Checkpoints between requests. |
| `--prompt-cache-every N` | 16384 | Checkpoint every N fresh prompt tokens. |
| `--prompt-cache-tail` | off | Extra checkpoint near prompt end. |
| `--prompt-cache-spread` | off | Spread checkpoints back from conversation end. |
| `--conversation-cache-mib N` | 0 | RAM budget for parked conversations. |
| `--memory-limit-mib N` | 0 | Engine RAM limit (used in G2). |

## MTP / speculative decoding

| Flag | Default | Effect |
|---|---|---|
| `--spec N` | - | Draft-layer verification window. Active: 4. |
| `--spec-min-p P` | - | Threshold for extending a verify window. Active: 0.5. |
| `--mtp DIR` | - | Draft layer path. Active: `D:\Strata-HotRod-data\mtp\rt`. |
| `--suffix-draft N` | 3 | Prompt-lookup drafts. |
| `--lookup-chain K` | 0 | Additional prompt-lookup drafts. |
| `--spec-prob-accept` / `--no-spec-prob-accept` | on | Probabilistic draft acceptance. |
| `--coupled-draft` / `--no-coupled-draft` | on | Coupled draft sampling. |
| `--mtp-q4 all\|proj\|head` | off | 4-bit draft projections/head. |

**Note:** the native IQ3_S pack requires `--spec >= 2`. Removing `--spec`/`--mtp`
makes the engine exit immediately with "native pack needs --native SHARD1,
--spec T (T >= 2) and --prefill CHUNK". MTP-off tests are therefore "not possible".

## Expert routing (HotRod-specific)

| Flag | Default | Effect |
|---|---|---|
| `--expert-profile P` | - | Preload VRAM tier from a profile. Active: `data\expert-profile.bin`. |
| `--expert-profile-save P` | off | Save learned expertise as a profile. |
| `--adapt-min-gain F` | 1.5 | Swap threshold of the adaptive tier. |
| `--adapt-async 1` | 0 | Swaps between verify windows (not bit-exact). |
| `--no-hit-poke` | off | A/B: disable driver poke after hit launch. |
| `--no-ple-prefetch` | off | A/B: read PLE rows one by one instead of PrefetchVirtualMemory. |
| `--no-pool` | off | CPU expert pool off (GPU-only floor). |
| `--pool-workers N` | 0 (all physical cores minus 1) | Number of pool workers. |
| `--pool-tasks N` | 0 | Batched CPU expert tasks per phase. |
| `--host-core first\|last\|sibling` | first | Host thread core (GPU interrupts). |
| `--aux-cpus off\|auto\|LIST` | off | Placement of remaining threads. |
| `--pool-affinity all\|auto\|p-cores` | all | Worker affinity. |
| `--mmap-experts` | off | A/B: back to MapViewOfFile instead of resident arena. |
| `--resident-experts` | off | Low-RAM mode (mmap + resident CPU experts). |

## PLE / SSD

| Flag | Default | Effect |
|---|---|---|
| `--ple-io direct\|mmap\|ram` | direct | SSD row reads / mapped / fully in RAM. |
| `--ple-row-cache N` | 1048576 | Row cache (90 B per row). |
| `--ple-inflight N` | 256 | Outstanding SSD reads. |
| `--no-ple` | off | Disable PLE layer entirely (diagnostic). |

## Context / sampling

| Flag | Default | Effect |
|---|---|---|
| `--max-context N` | 4096 | KV/state capacity. Active: 131072. |
| `--rope-scaling none\|linear\|yarn` | model file | Context extension. |
| `--temperature F`, `--top-k N`, `--top-p F`, `--seed S` | - | Sampling (request-level overrides available). |

## Relevant environment variables (active config)

| Variable | Active value | Meaning |
|---|---|---|
| `STRATA_HC_Q8` | 1 | Q8_0 hyperconnection verify read. |
| `STRATA_ROUTE_TAIL_SKIP` | 0 | Router tail skip. |
| `STRATA_RESIDENT_HEADROOM_GIB` | 6 | Headroom for resident experts. |
| `STRATA_ARENA_PIN_GIB` | 40 | Cap for CUDA pinning of the arena. |
| `STRATA_KVA` | 1 | KV arena. |
| `STRATA_ROUTE_RESIDENT` | 1e30 | Residency bias margin. |
| `STRATA_ROUTE_RESIDENT_RANKS` | 3-9 | Affected ranks. |
| `STRATA_ROUTE_RESIDENT_EDGE` | 1 | Edge experiment. |
| `STRATA_SWAP2_MAX` | 2 | SWAP2 limit. |
| `STRATA_SWAP2_GAP` | 1 | SWAP2 gap. |
| `STRATA_KV_GROW_INIT` | 4096 | Initial KV-grow size. |
| `STRATA_LA_LEARN` | 1 | Look-ahead learning. |
| `STRATA_MASK` | 0.05 | Expert masking (from log). |
| `STRATA_PREFILL_CPU_SHARE` | auto | CPU share of prefill (only if commit limit allows). |

## Not automatable

- `--gpu-only-full`, `--graph-only`: diagnostic GPU floors, not server measurements.
- Debug flags (`--dump-*`, `--sync-every-layer`, `--check-logits`) change the measurement path.
- `--control-vector*`: permitted, but no performance switch without a model file.
