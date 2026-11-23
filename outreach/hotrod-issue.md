# Draft for an issue in sangharshadhyeta/Strata-HotRod

Title: Windows/WDDM: `--vram-reserve-mib 0` causes a ~74 s stall on the first request

## Description

With the setup default (`--vram-reserve-mib 0`), the engine reports after load:
"0 MiB of VRAM free with everything loaded - LOW: requests may stall". On an
RTX 3090 (24 GB) + 96 GB RAM + Windows 10, the first chat request after startup
took **73.6 s**. With 512 MiB it took **2.2 s**, with 700 MiB **2.5 s**. The
decode median was highest at 512 MiB (82.2 vs 72-79 tok/s), although the sweep
was not statistically significant (p=0.22, n=8 per variant).

## Reproduction

1. Start the engine with the native IQ3_S pack and `--vram-reserve-mib 0`.
2. Send one chat request with ~80 prompt tokens / 96 output tokens; measure wall time.
3. Repeat with 512 and 700 MiB.

## Expected

The first request after load should not be blocked by WDDM overcommit.

## Additional findings

- **Learning curve:** with empty learning data over 150 requests there was no
  monotonic improvement; decode oscillated between 68 and 89 tok/s
  (prompt-class dependent). The look-ahead learner occasionally reported
  "rename failed" when saving its predictor binary.
- **SSD path:** despite 96 GB RAM, 0% demand reads and 0% in-flight read waits
  in the decode timeline; the bottleneck is CPU experts (~45%) plus GPU (~53%).
- **Resident experts:** about 8,000-9,000 of 24,576, 2-5 swaps per round; no
  correlation with decode (r=0.03, p=0.76).
- **Telemetry:** Record via `POST /v1/monitor/timeline` and `/metrics` polling
  caused no measurable overhead.

Full data, runner and telemetry: see the repository URL in
`outreach/repochad-message.md`.

**Not posted automatically.**
