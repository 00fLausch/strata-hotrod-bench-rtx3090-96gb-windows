# Nachricht an RepoChad (englisch, manuell senden)

Hi RepoChad,

I ran a systematic benchmark of Strata-HotRod with Qwen3.8-Flash-Next IQ3_S on a
single RTX 3090 (24 GB) + 96 GB DDR4 under Windows 10, and published all data,
the runner, telemetry and charts here:

https://github.com/00fLausch/strata-hotrod-bench-rtx3090-96gb-windows

Three findings I thought you'd find interesting:

1. **One reserve value changes the first-token experience.** The stock config
   uses `--vram-reserve-mib 0`; the engine reports 0 MiB free VRAM after load
   and the first request took **73.6 seconds**. With 512 MiB it took 2.2 s.
   The decode median was also highest at 512 MiB (82 tok/s), though the sweep
   was not statistically significant.

2. **It's a CPU-expert workload, not an SSD workload.** Even with 96 GB RAM,
   the decode timeline shows ~53% GPU-alone/host-waiting and ~45% CPU experts,
   with 0% demand reads. More VRAM reserve just gives the expert cache fewer
   slots — it doesn't unlock more speed.

3. **Prefill chunk size matters at 32K.** `auto:32768` reached 2,539 tok/s vs
   1,782 tok/s with `auto:4096` (TTFT 11.8 s vs 16.8 s). At 128K the picture
   is mixed. 200K context actually worked at ~52 tok/s decode.

I also ran a 90-minute soak (2,905 requests, zero errors, flat RAM) and live
monitor telemetry throughout. If it's useful, I can run targeted tests for
your setup — e.g. a different GPU/RAM split, WSL2 vs Windows, or a specific
MTP/spec configuration.

Thanks for the great content,
[NAME]
