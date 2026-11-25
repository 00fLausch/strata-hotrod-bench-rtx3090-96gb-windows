# Result tables

All values: median [IQR], bootstrap 95% CI. Decode tok/s from engine timings.

| Test | Block | Reserve | Decode Median [IQR] | 95% CI | Prefill Median | TTFT | Slots auto→final | Shrinks | Experts in VRAM | Swaps/round | Cause (telemetry) | n | Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| A1_current | A1 | 512 | — — | — | — | — | —→— | — | — | — | no telemetry | 0 | complete |
| A1_default | A1 | 512 | — — | — | — | — | —→— | — | — | — | no telemetry | 0 | complete |
| A2_noise_end | A2_3 | 512 | 73.7 [60.6–86.1] | [60.8–86.0] | 286.7 | 0.33 | 6737→8791 | 0 | 8791 | 2.2 | GPU-bound: SSD path essentially unused; 2.2 Swaps/round; 8791 Experts in VRAM | 16 | complete |
| A2_noise_middle | A2_2 | 512 | 74.7 [64.6–91.8] | [65.0–91.4] | 311.2 | 0.31 | 6737→8791 | 0 | 8791 | 2.1 | GPU-bound: SSD path essentially unused; 2.1 Swaps/round; 8791 Experts in VRAM | 16 | complete |
| A2_noise_start | A2_1 | 512 | 66.6 [56.7–79.2] | [57.0–79.2] | 248.0 | 0.39 | 6737→8791 | 0 | 8791 | 2.1 | GPU-bound: SSD path essentially unused; 2.1 Swaps/round; 8791 Experts in VRAM | 16 | complete |
| A3_official_vs_hotrod | A3 | 512 | — — | — | — | — | —→— | — | — | — | no telemetry | 0 | complete |
| B1_reserve_1024 | B1 | 1024 | 77.3 [68.7–88.0] | [71.5–86.7] | 314.1 | 0.33 | 6535→8530 | 0 | 8530 | 4.1 | GPU-bound: SSD path essentially unused; 4.1 Swaps/round; 8530 Experts in VRAM | 32 | complete |
| B1_reserve_1536 | B1 | 1536 | 78.3 [66.8–89.4] | [68.5–85.6] | 302.1 | 0.34 | 6333→8264 | 0 | 8264 | 3.8 | GPU-bound: SSD path essentially unused; 3.8 Swaps/round; 8264 Experts in VRAM | 32 | complete |
| B1_reserve_2048 | B1 | 2048 | 76.2 [65.1–82.4] | [68.2–80.6] | 284.6 | 0.38 | 6132→7998 | 0 | 7998 | 4.6 | GPU-bound: SSD path essentially unused; 4.6 Swaps/round; 7998 Experts in VRAM | 32 | complete |
| B1_reserve_256 | B1 | 256 | 76.4 [67.5–91.4] | [72.2–87.3] | 319.0 | 0.33 | 6837→8920 | 0 | 8920 | 2.8 | GPU-bound: SSD path essentially unused; 2.8 Swaps/round; 8920 Experts in VRAM | 32 | complete |
| B1_reserve_2560 | B1 | 2560 | 74.7 [65.5–80.0] | [66.7–78.5] | 271.8 | 0.38 | 5930→7733 | 0 | 7733 | 4.6 | GPU-bound: SSD path essentially unused; 4.6 Swaps/round; 7733 Experts in VRAM | 32 | complete |
| B1_reserve_3072 | B1 | 3072 | 72.0 [63.4–80.9] | [64.7–77.6] | 266.1 | 0.40 | 5728→7465 | 0 | 7465 | 4.6 | GPU-bound: SSD path essentially unused; 4.6 Swaps/round; 7465 Experts in VRAM | 32 | complete |
| B1_reserve_4096 | B1 | 4096 | 74.9 [67.5–90.4] | [71.1–84.5] | 301.8 | 0.34 | 5325→6940 | 0 | 6940 | 4.8 | GPU-bound: SSD path essentially unused; 4.8 Swaps/round; 6940 Experts in VRAM | 32 | complete |
| B1_reserve_512 | B1_0 | 512 | 82.2 [69.6–94.1] | [70.9–90.7] | 311.6 | 0.34 | 6737→8791 | 0 | 8791 | 2.6 | GPU-bound: SSD path essentially unused; 2.6 Swaps/round; 8791 Experts in VRAM | 32 | complete |
| B1_reserve_700 | B1 | 700 | 78.7 [69.8–90.8] | [73.4–88.2] | 317.3 | 0.34 | 6663→8696 | 0 | 8696 | 3.5 | GPU-bound: SSD path essentially unused; 3.5 Swaps/round; 8696 Experts in VRAM | 32 | complete |
| B6_stability_40 | B6 | 512 | 78.5 [68.3–89.7] | [72.1–86.9] | 322.2 | 0.33 | 6737→8791 | 0 | 8791 | 3.0 | GPU-bound: SSD path essentially unused; 3.0 Swaps/round; 8791 Experts in VRAM | 40 | complete |
| C1_auto_16384_128k | C1 | 512 | 53.0 [35.3–53.1] | [32.8–63.1] | 2196.9 | 52.28 | 6737→8791 | 0 | — | — | GPU-bound: SSD path essentially unused | 5 | complete |
| C1_auto_16384_32k | C1 | 512 | 93.5 [86.6–96.4] | [86.1–96.5] | 1674.7 | 17.88 | 6737→8791 | 0 | 8791 | 4.9 | GPU-bound: SSD path essentially unused; 4.9 Swaps/round; 8791 Experts in VRAM | 8 | complete |
| C1_auto_32768_128k | C1 | 512 | 71.4 [68.5–71.5] | [51.2–74.6] | 1664.9 | 68.94 | 6737→8791 | 0 | 8791 | 7.5 | GPU-bound: SSD path essentially unused; 7.5 Swaps/round; 8791 Experts in VRAM | 5 | complete |
| C1_auto_32768_32k | C1 | 512 | 92.4 [91.2–97.0] | [88.7–97.6] | 2538.6 | 11.82 | 6737→8791 | 0 | 8791 | 4.0 | GPU-bound: SSD path essentially unused; 4.0 Swaps/round; 8791 Experts in VRAM | 8 | complete |
| C1_auto_4096_128k | C1 | 512 | 51.6 [29.3–60.2] | [26.2–63.1] | 2165.3 | 53.02 | 6737→8791 | 0 | — | — | GPU-bound: SSD path essentially unused | 5 | complete |
| C1_auto_4096_32k | C1 | 512 | 96.3 [93.8–98.1] | [92.7–100.4] | 1782.3 | 16.82 | 6737→8791 | 0 | 8791 | 4.8 | GPU-bound: SSD path essentially unused; 4.8 Swaps/round; 8791 Experts in VRAM | 8 | complete |
| C1_auto_8192_128k | C1 | 512 | 52.0 [44.2–62.5] | [35.5–63.5] | 2193.2 | 52.34 | 6737→8791 | 0 | 8791 | 5.8 | GPU-bound: SSD path essentially unused; 5.8 Swaps/round; 8791 Experts in VRAM | 5 | complete |
| C1_auto_8192_32k | C1 | 512 | 91.5 [90.6–92.4] | [89.6–93.5] | 1791.0 | 16.73 | 6737→8791 | 0 | 8791 | 5.5 | GPU-bound: SSD path essentially unused; 5.5 Swaps/round; 8791 Experts in VRAM | 8 | complete |
| C2_auto_16384_r2048 | C2 | 2048 | 94.5 [86.8–95.4] | [35.5–98.5] | 1686.5 | 17.77 | 6132→7998 | 0 | 7998 | 8.2 | GPU-bound: SSD path essentially unused; 8.2 Swaps/round; 7998 Experts in VRAM | 5 | complete |
| C2_auto_16384_r512 | C2 | 512 | 114.4 [113.1–115.9] | [108.7–116.8] | 1691.4 | 17.70 | 6737→8791 | 0 | 8791 | 8.0 | GPU-bound: SSD path essentially unused; 8.0 Swaps/round; 8791 Experts in VRAM | 5 | complete |
| C2_auto_4096_r2048 | C2 | 2048 | 90.7 [81.2–92.2] | [37.5–93.5] | 1782.3 | 16.81 | 6132→7998 | 0 | 7998 | 10.5 | GPU-bound: SSD path essentially unused; 10.5 Swaps/round; 7998 Experts in VRAM | 5 | complete |
| C2_auto_4096_r512 | C2 | 512 | 94.8 [94.1–94.9] | [93.8–99.3] | 1789.2 | 16.75 | 6737→8791 | 0 | 8791 | 7.1 | GPU-bound: SSD path essentially unused; 7.1 Swaps/round; 8791 Experts in VRAM | 5 | complete |
| C3_decode_after_128k | C3 | 512 | 62.4 [61.7–63.5] | [59.8–64.0] | 312.5 | 0.31 | 6737→8791 | 0 | 8791 | 3.2 | GPU-bound: SSD path essentially unused; 3.2 Swaps/round; 8791 Experts in VRAM | 5 | complete |
| C3_decode_after_short | C3 | 512 | 65.9 [65.2–67.7] | [62.2–68.4] | 290.9 | 0.34 | 6737→8791 | 0 | 8791 | 1.7 | GPU-bound: SSD path essentially unused; 1.7 Swaps/round; 8791 Experts in VRAM | 5 | complete |
| D1_ctx_128k | D1 | 512 | 53.7 [44.9–58.4] | [33.4–65.6] | 2202.3 | 52.14 | 6737→8791 | 0 | 8791 | 4.5 | GPU-bound: SSD path essentially unused; 4.5 Swaps/round; 8791 Experts in VRAM | 8 | complete |
| D1_ctx_16k | D1 | 512 | 92.5 [87.9–99.5] | [84.5–100.7] | 2444.1 | 6.16 | 6737→8791 | 0 | 8791 | 8.0 | GPU-bound: SSD path essentially unused; 8.0 Swaps/round; 8791 Experts in VRAM | 8 | complete |
| D1_ctx_200k | D1 | 512 | 52.3 [43.0–55.4] | [33.7–58.5] | 2155.7 | 85.66 | 6647→8674 | 0 | — | — | GPU-bound: SSD path essentially unused | 3 | complete |
| D1_ctx_32k | D1 | 512 | 86.8 [76.1–89.8] | [76.0–90.1] | 1692.9 | 17.70 | 6737→8791 | 0 | 8791 | 4.1 | GPU-bound: SSD path essentially unused; 4.1 Swaps/round; 8791 Experts in VRAM | 8 | complete |
| D1_ctx_4k | D1 | 512 | 86.8 [84.1–87.8] | [82.7–89.1] | 1881.9 | 1.97 | 6737→8791 | 0 | 8791 | 6.1 | GPU-bound: SSD path essentially unused; 6.1 Swaps/round; 8791 Experts in VRAM | 8 | complete |
| D1_ctx_64k | D1 | 512 | 71.4 [65.4–76.8] | [64.2–77.5] | 1931.1 | 31.05 | 6737→8791 | 0 | — | — | GPU-bound: SSD path essentially unused | 8 | complete |
| D2_maxctx_131072 | D2 | 512 | 78.7 [67.3–91.2] | [68.0–90.0] | 321.9 | 0.33 | 6737→8791 | 0 | 8791 | 4.0 | GPU-bound: SSD path essentially unused; 4.0 Swaps/round; 8791 Experts in VRAM | 20 | complete |
| D2_maxctx_262144 | D2 | 512 | 79.5 [66.4–90.6] | [67.1–90.2] | 305.8 | 0.34 | 6647→8674 | 0 | 8674 | 3.8 | GPU-bound: SSD path essentially unused; 3.8 Swaps/round; 8674 Experts in VRAM | 20 | complete |
| D3_kv_fp16 | D3 | 512 | 83.5 [66.1–88.6] | [69.7–88.2] | 306.7 | 0.34 | 6578→8585 | 0 | 8585 | 4.9 | GPU-bound: SSD path essentially unused; 4.9 Swaps/round; 8585 Experts in VRAM | 25 | complete |
| D3_kv_int8 | D3 | 512 | 82.4 [70.7–94.6] | [71.7–91.7] | 325.3 | 0.34 | 6737→8791 | 0 | 8791 | 4.2 | GPU-bound: SSD path essentially unused; 4.2 Swaps/round; 8791 Experts in VRAM | 25 | complete |
| D3_kv_k8v4 | D3 | 512 | 83.6 [71.4–93.2] | [71.4–91.2] | 319.3 | 0.34 | 6772→8836 | 0 | 8836 | 4.2 | GPU-bound: SSD path essentially unused; 4.2 Swaps/round; 8836 Experts in VRAM | 25 | complete |
| D3_kv_q4_0 | D3 | 512 | 82.5 [68.7–89.7] | [70.4–87.8] | 320.3 | 0.34 | 6813→8889 | 0 | 8889 | 4.3 | GPU-bound: SSD path essentially unused; 4.3 Swaps/round; 8889 Experts in VRAM | 25 | complete |
| D4_output_2048 | D4 | 512 | 62.6 [60.6–63.0] | [58.6–64.5] | 300.4 | 0.33 | 6737→8791 | 0 | 8791 | 0.8 | GPU-bound: SSD path essentially unused; 0.8 Swaps/round; 8791 Experts in VRAM | 5 | complete |
| D4_output_512 | D4 | 512 | 63.0 [62.6–66.0] | [61.2–67.3] | 280.2 | 0.34 | 6737→8791 | 0 | 8791 | 0.8 | GPU-bound: SSD path essentially unused; 0.8 Swaps/round; 8791 Experts in VRAM | 5 | complete |
| D4_output_8192 | D4 | 512 | 61.8 [61.0–62.0] | [60.1–64.7] | 296.1 | 0.33 | 6737→8791 | 0 | 8791 | 1.0 | GPU-bound: SSD path essentially unused; 1.0 Swaps/round; 8791 Experts in VRAM | 5 | complete |
| D5_multiturn_long_128k | D5 | 512 | 63.7 [63.2–65.6] | [59.0–65.6] | 298.6 | 0.33 | 6737→8791 | 0 | 8791 | 3.8 | GPU-bound: SSD path essentially unused; 3.8 Swaps/round; 8791 Experts in VRAM | 5 | complete |
| D5_multiturn_long_32k | D5 | 512 | 62.3 [61.8–62.5] | [58.6–62.7] | 308.1 | 0.33 | 6737→8791 | 0 | 8791 | 3.3 | GPU-bound: SSD path essentially unused; 3.3 Swaps/round; 8791 Experts in VRAM | 5 | complete |
| D5_multiturn_long_4k | D5 | 512 | 65.7 [64.7–68.3] | [62.2–69.4] | 302.9 | 0.33 | 6737→8791 | 0 | 8791 | 3.3 | GPU-bound: SSD path essentially unused; 3.3 Swaps/round; 8791 Experts in VRAM | 5 | complete |
| D6_convcache_0 | D6 | 512 | 65.0 [64.3–66.3] | [63.4–68.0] | 314.6 | 0.31 | 6737→8791 | 0 | 8791 | 2.5 | GPU-bound: SSD path essentially unused; 2.5 Swaps/round; 8791 Experts in VRAM | 8 | complete |
| D6_convcache_2048 | D6 | 512 | 66.1 [62.3–67.7] | [60.1–67.7] | 305.3 | 0.32 | 6737→8791 | 0 | 8791 | 3.0 | GPU-bound: SSD path essentially unused; 3.0 Swaps/round; 8791 Experts in VRAM | 8 | complete |
| D6_convcache_512 | D6 | 512 | 62.5 [61.5–65.8] | [60.8–66.6] | 310.1 | 0.33 | 6737→8791 | 0 | 8791 | 2.2 | GPU-bound: SSD path essentially unused; 2.2 Swaps/round; 8791 Experts in VRAM | 8 | complete |
| D7_len_2k | D7 | 512 | 103.8 [99.9–105.0] | [96.8–105.9] | 1499.7 | 1.23 | 6737→8791 | 0 | 8791 | 5.9 | GPU-bound: SSD path essentially unused; 5.9 Swaps/round; 8791 Experts in VRAM | 8 | complete |
| D7_len_500 | D7 | 512 | 91.4 [90.6–92.9] | [89.3–93.6] | 782.6 | 0.55 | 6737→8791 | 0 | 8791 | 3.2 | GPU-bound: SSD path essentially unused; 3.2 Swaps/round; 8791 Experts in VRAM | 8 | complete |
| D7_len_84 | D7 | 512 | 65.4 [62.8–67.3] | [62.4–67.8] | 294.2 | 0.33 | 6737→8791 | 0 | 8791 | 2.1 | GPU-bound: SSD path essentially unused; 2.1 Swaps/round; 8791 Experts in VRAM | 8 | complete |
| D7_len_8k | D7 | 512 | 111.9 [107.4–116.5] | [106.9–119.1] | 2275.2 | 3.33 | 6737→8791 | 0 | 8791 | 3.9 | GPU-bound: SSD path essentially unused; 3.9 Swaps/round; 8791 Experts in VRAM | 8 | complete |
| E1_learn_from_empty | E1 | 512 | 79.4 [66.2–92.4] | [70.5–86.8] | 316.9 | 0.31 | 6737→8791 | 0 | — | — | no telemetry | 300 | complete |
| E3_train_chat_measure_coding | E3 | 512 | 93.1 [88.4–96.8] | [91.5–95.1] | 327.2 | 0.31 | 6737→8791 | 0 | — | — | no telemetry | 80 | complete |
| E3_train_coding_measure_chat | E3 | 512 | 70.3 [67.4–75.3] | [69.7–72.0] | 223.6 | 0.40 | 6737→8791 | 0 | — | — | no telemetry | 160 | complete |
| E4_de_vs_en | E4 | 512 | 69.8 [66.7–74.4] | [67.0–73.9] | 223.9 | 0.40 | 6737→8791 | 0 | 8791 | 1.2 | GPU-bound: SSD path essentially unused; 1.2 Swaps/round; 8791 Experts in VRAM | 16 | complete |
| E5_persist_after_restart | E5 | 512 | 66.1 [64.5–68.2] | [64.8–67.5] | 301.5 | 0.33 | 6737→8791 | 0 | — | — | no telemetry | 40 | complete |
| F1_expert_cache_per_layer | F1 | 512 | 82.5 [69.8–93.1] | [72.1–88.7] | 313.0 | 0.34 | 6737→8791 | 0 | 8791 | 3.2 | GPU-bound: SSD path essentially unused; 3.2 Swaps/round; 8791 Experts in VRAM | 32 | complete |
| F1_hc_q8_off | F1 | 512 | 83.4 [71.0–94.1] | [77.6–91.0] | 341.9 | 0.30 | 6579→8587 | 0 | 8587 | 3.7 | GPU-bound: SSD path essentially unused; 3.7 Swaps/round; 8587 Experts in VRAM | 32 | complete |
| F1_kv_grow | F1 | 512 | 77.5 [71.3–87.8] | [72.8–86.2] | 310.0 | 0.34 | 6737→8791 | 0 | 8791 | 3.3 | GPU-bound: SSD path essentially unused; 3.3 Swaps/round; 8791 Experts in VRAM | 32 | complete |
| F1_kva_off | F1 | 512 | 80.7 [70.0–90.1] | [71.8–88.8] | 307.9 | 0.34 | 6737→8791 | 0 | 8791 | 3.0 | GPU-bound: SSD path essentially unused; 3.0 Swaps/round; 8791 Experts in VRAM | 32 | complete |
| F1_la_learn_off | F1 | 512 | 90.0 [76.2–103.0] | [79.6–99.8] | 322.4 | 0.34 | 6737→8791 | 0 | 8791 | 3.3 | GPU-bound: SSD path essentially unused; 3.3 Swaps/round; 8791 Experts in VRAM | 32 | complete |
| F1_no_hit_poke | F1 | 512 | 81.3 [68.9–91.3] | [72.2–89.4] | 331.0 | 0.31 | 6737→8791 | 0 | 8791 | 3.6 | GPU-bound: SSD path essentially unused; 3.6 Swaps/round; 8791 Experts in VRAM | 32 | complete |
| F1_no_ple_prefetch | F1 | 512 | 77.8 [69.9–94.7] | [71.5–92.1] | 316.3 | 0.34 | 6737→8791 | 0 | 8791 | 3.2 | GPU-bound: SSD path essentially unused; 3.2 Swaps/round; 8791 Experts in VRAM | 32 | complete |
| F1_no_pool | F1 | 512 | 87.2 [69.2–99.1] | [76.4–95.7] | 333.0 | 0.31 | 6737→8791 | 0 | 8791 | 3.4 | GPU-bound: SSD path essentially unused; 3.4 Swaps/round; 8791 Experts in VRAM | 32 | complete |
| F1_ple_io_mmap | F1 | 512 | 80.6 [69.4–95.8] | [72.7–91.8] | 339.1 | 0.30 | 6737→8791 | 0 | 8791 | 3.5 | GPU-bound: SSD path essentially unused; 3.5 Swaps/round; 8791 Experts in VRAM | 32 | complete |
| F1_ple_io_ram | F1 | 512 | 81.1 [68.7–92.4] | [72.7–87.3] | 304.4 | 0.34 | 6737→8791 | 0 | 8791 | 3.5 | GPU-bound: SSD path essentially unused; 3.5 Swaps/round; 8791 Experts in VRAM | 32 | complete |
| F1_prefill_head_alias | F1 | 512 | 78.7 [69.5–92.0] | [70.7–90.5] | 309.6 | 0.33 | 6737→8791 | 0 | 8791 | 2.7 | GPU-bound: SSD path essentially unused; 2.7 Swaps/round; 8791 Experts in VRAM | 32 | complete |
| F1_prompt_cache_0 | F1 | 512 | 84.4 [71.5–93.6] | [74.4–92.2] | 328.4 | 0.31 | 6737→8791 | 0 | 8791 | 3.5 | GPU-bound: SSD path essentially unused; 3.5 Swaps/round; 8791 Experts in VRAM | 32 | complete |
| F1_route_resident_off | F1 | 512 | 74.9 [72.1–81.2] | [73.4–79.7] | 177.3 | 0.55 | 6737→8791 | 0 | 8791 | 22.8 | GPU-bound: SSD path essentially unused; 22.8 Swaps/round; 8791 Experts in VRAM | 32 | complete |
| F1_suffix_draft_0 | F1 | 512 | 84.4 [70.2–91.9] | [73.9–90.5] | 315.9 | 0.33 | 6738→8793 | 0 | 8793 | 3.3 | GPU-bound: SSD path essentially unused; 3.3 Swaps/round; 8793 Experts in VRAM | 32 | complete |
| F1_swap2_off | F1 | 512 | 86.3 [73.6–98.9] | [76.6–97.2] | 335.7 | 0.31 | 6737→8791 | 0 | 8791 | 3.2 | GPU-bound: SSD path essentially unused; 3.2 Swaps/round; 8791 Experts in VRAM | 32 | complete |
| F2_mtp_off | F2 | 512 | 50.2 [49.0–51.7] | [49.4–51.1] | 288.0 | 0.34 | 7154→9109 | 1 | 9109 | 0.6 | GPU-bound: SSD path essentially unused; 0.6 Swaps/round; 9109 Experts in VRAM | 32 | complete |
| F2_spec_2 | F2 | 512 | 76.5 [72.5–79.3] | [73.7–78.9] | 342.5 | 0.30 | 6738→8793 | 0 | 8793 | 1.7 | GPU-bound: SSD path essentially unused; 1.7 Swaps/round; 8793 Experts in VRAM | 32 | complete |
| F2_spec_6 | F2 | 512 | 72.6 [68.2–90.3] | [70.7–86.5] | 342.5 | 0.31 | 6736→8790 | 0 | 8790 | 3.4 | GPU-bound: SSD path essentially unused; 3.4 Swaps/round; 8790 Experts in VRAM | 32 | complete |
| F2_temp_0 | F2 | 512 | 84.8 [77.2–96.0] | [80.1–91.1] | 338.6 | 0.31 | 6737→8791 | 0 | 8791 | 2.3 | GPU-bound: SSD path essentially unused; 2.3 Swaps/round; 8791 Experts in VRAM | 32 | complete |
| F2_temp_1 | F2 | 512 | 84.0 [71.1–97.8] | [72.5–93.2] | 335.6 | 0.30 | 6737→8791 | 0 | 8791 | 2.8 | GPU-bound: SSD path essentially unused; 2.8 Swaps/round; 8791 Experts in VRAM | 32 | complete |
| F3_reasoning_high | F3 | 512 | 78.1 [73.7–89.1] | [74.1–84.1] | 353.6 | 0.38 | 6737→8791 | 0 | 8791 | 1.7 | GPU-bound: SSD path essentially unused; 1.7 Swaps/round; 8791 Experts in VRAM | 20 | complete |
| F3_reasoning_low | F3 | 512 | 90.6 [84.1–97.2] | [84.6–95.7] | 351.6 | 0.34 | 6737→8791 | 0 | 8791 | 2.9 | GPU-bound: SSD path essentially unused; 2.9 Swaps/round; 8791 Experts in VRAM | 20 | complete |
| F3_reasoning_medium | F3 | 512 | 88.2 [86.0–92.7] | [86.2–90.6] | 287.3 | 0.34 | 6737→8791 | 0 | 8791 | 3.1 | GPU-bound: SSD path essentially unused; 3.1 Swaps/round; 8791 Experts in VRAM | 20 | complete |
| F3_reasoning_none | F3 | 512 | 83.7 [71.7–96.4] | [72.5–96.0] | 311.0 | 0.33 | 6737→8791 | 0 | 8791 | 2.6 | GPU-bound: SSD path essentially unused; 2.6 Swaps/round; 8791 Experts in VRAM | 20 | complete |
| F4_aux_cpus_auto | F4 | 512 | 77.6 [68.9–90.1] | [70.2–89.2] | 318.0 | 0.34 | 6737→8791 | 0 | 8791 | 3.7 | GPU-bound: SSD path essentially unused; 3.7 Swaps/round; 8791 Experts in VRAM | 20 | complete |
| F4_host_core_last | F4 | 512 | 77.0 [68.0–89.0] | [69.3–88.2] | 344.6 | 0.30 | 6737→8791 | 0 | 8791 | 4.5 | GPU-bound: SSD path essentially unused; 4.5 Swaps/round; 8791 Experts in VRAM | 20 | complete |
| F4_pool_workers_4 | F4 | 512 | 82.4 [69.1–90.7] | [72.5–90.3] | 303.3 | 0.34 | 6737→8791 | 0 | 8791 | 3.9 | GPU-bound: SSD path essentially unused; 3.9 Swaps/round; 8791 Experts in VRAM | 20 | complete |
| F4_pool_workers_8 | F4 | 512 | 77.3 [68.2–90.0] | [70.3–87.7] | 290.9 | 0.36 | 6737→8791 | 0 | 8791 | 3.9 | GPU-bound: SSD path essentially unused; 3.9 Swaps/round; 8791 Experts in VRAM | 20 | complete |
| F5_best_combination | F5 | 2048 | 77.3 [69.3–92.4] | [70.7–89.1] | 309.1 | 0.34 | 6132→7998 | 0 | 7998 | 3.7 | GPU-bound: SSD path essentially unused; 3.7 Swaps/round; 7998 Experts in VRAM | 32 | complete |
| G2_ram_limit_30720 | G2 | 512 | 76.6 [64.2–85.6] | [64.7–84.3] | 306.1 | 0.34 | 6737→8791 | 0 | 8791 | 3.7 | GPU-bound: SSD path essentially unused; 3.7 Swaps/round; 8791 Experts in VRAM | 20 | complete |
| G2_ram_limit_49152 | G2 | 512 | 79.5 [65.4–89.1] | [67.0–88.4] | 298.3 | 0.34 | 6737→8791 | 0 | 8791 | 3.7 | GPU-bound: SSD path essentially unused; 3.7 Swaps/round; 8791 Experts in VRAM | 20 | complete |
| G2_ram_limit_65536 | G2 | 512 | 79.1 [68.8–91.2] | [70.0–89.8] | 307.1 | 0.34 | 6737→8791 | 0 | 8791 | 4.2 | GPU-bound: SSD path essentially unused; 4.2 Swaps/round; 8791 Experts in VRAM | 20 | complete |
| G3_defender | G4 | 512 | — — | — | — | — | —→— | — | — | — | no telemetry | 0 | failed |
| H1_power_200W | H1 | 512 | — — | — | — | — | —→— | — | — | — | no telemetry | 0 | failed |
| H1_power_250W | H1 | 512 | — — | — | — | — | —→— | — | — | — | no telemetry | 0 | failed |
| H1_power_300W | H1 | 512 | — — | — | — | — | —→— | — | — | — | no telemetry | 0 | failed |
| H1_power_350W | H1 | 512 | — — | — | — | — | —→— | — | — | — | no telemetry | 0 | failed |
| H2_power_plan | H2 | 512 | 86.4 [71.0–93.9] | [72.9–93.1] | 328.7 | 0.33 | 6737→8791 | 0 | 8791 | 4.0 | GPU-bound: SSD path essentially unused; 4.0 Swaps/round; 8791 Experts in VRAM | 20 | complete |
| I1_needle_128k | I1 | 512 | — — | — | — | — | —→— | — | — | — | no telemetry | 0 | complete |
| I1_needle_32k | I1 | 512 | — — | — | — | — | —→— | — | — | — | no telemetry | 0 | complete |
| I2_parity_mtp_off | I2 | 512 | 52.6 [50.7–54.2] | [50.5–54.5] | 294.4 | 0.34 | 7154→9112 | 1 | 9112 | 0.5 | GPU-bound: SSD path essentially unused; 0.5 Swaps/round; 9112 Experts in VRAM | 10 | complete |
| I2_parity_mtp_on | I2 | 512 | 77.3 [67.9–92.5] | [66.9–93.6] | 311.6 | 0.33 | 6737→8791 | 0 | 8791 | 1.7 | GPU-bound: SSD path essentially unused; 1.7 Swaps/round; 8791 Experts in VRAM | 10 | complete |
| J1_parallel_1 | J1 | 512 | — — | — | — | — | —→— | — | — | — | no telemetry | 5 | complete |
| J1_parallel_2 | J1 | 512 | — — | — | — | — | —→— | — | — | — | no telemetry | 5 | complete |
| J1_parallel_4 | J1 | 512 | — — | — | — | — | —→— | — | — | — | no telemetry | 5 | complete |
| J2_soak_90min | J2 | 512 | 83.1 [72.5–95.8] | [82.0–84.1] | — | — | —→— | — | — | — | no telemetry | 2905 | complete |
| J3_abort_prefill | J3 | 512 | — — | — | — | — | —→— | — | — | — | no telemetry | 0 | complete |
| J3_oversized | J3 | 512 | — — | — | — | — | —→— | — | — | — | no telemetry | 0 | complete |
| K1_vram_elastic_off | K | 512 | 79.4 [74.0–97.7] | [74.7–96.8] | 335.3 | 0.32 | 6737→8791 | 0 | 8791 | 4.2 | GPU-bound: SSD path essentially unused; 4.2 Swaps/round; 8791 Experts in VRAM | 20 | complete |
| K2_config_reserve_2048 | K | 512 | 80.3 [68.0–90.6] | [69.2–89.0] | 308.3 | 0.33 | 6737→8791 | 0 | 8791 | 3.5 | GPU-bound: SSD path essentially unused; 3.5 Swaps/round; 8791 Experts in VRAM | 20 | complete |
| K4_vision_off |  | 512 | — — | — | — | — | —→— | — | — | — | no telemetry | 0 | failed |
| K6_expert_cache_off | K | 512 | 77.2 [67.0–88.5] | [68.4–87.5] | 306.9 | 0.34 | 6737→8791 | 0 | 8791 | 3.9 | GPU-bound: SSD path essentially unused; 3.9 Swaps/round; 8791 Experts in VRAM | 20 | complete |
| K7_kv_grow_long | K | 512 | 95.4 [95.3–96.2] | [95.0–96.4] | 1689.7 | 17.73 | 6737→8791 | 0 | 8791 | 6.4 | GPU-bound: SSD path essentially unused; 6.4 Swaps/round; 8791 Experts in VRAM | 5 | complete |
| T1_record_off | T1_3 | 512 | 78.6 [72.3–91.5] | [73.0–87.3] | 316.6 | 0.33 | 6737→8791 | 0 | 8791 | 3.1 | GPU-bound: SSD path essentially unused; 3.1 Swaps/round; 8791 Experts in VRAM | 32 | complete |
| T1_record_on | T1_4 | 512 | 80.7 [68.5–92.7] | [71.5–90.5] | 315.5 | 0.34 | 6737→8791 | 0 | 8791 | 3.6 | GPU-bound: SSD path essentially unused; 3.6 Swaps/round; 8791 Experts in VRAM | 32 | complete |
| T1_recorder_off | T1_1 | 512 | 77.8 [69.5–93.7] | [70.8–89.2] | 308.7 | 0.33 | 6737→8791 | 0 | — | — | no telemetry | 32 | complete |
| T1_recorder_on | T1_2 | 512 | 82.3 [68.9–90.1] | [75.1–87.1] | 312.7 | 0.34 | 6737→8791 | 0 | 8791 | 3.6 | GPU-bound: SSD path essentially unused; 3.6 Swaps/round; 8791 Experts in VRAM | 32 | complete |
| TL_chat_de | TL | 512 | 63.4 [62.7–64.1] | [62.0–64.7] | 283.3 | 0.34 | 6737→8791 | 0 | 8791 | 1.8 | GPU-bound: SSD path essentially unused; 1.8 Swaps/round; 8791 Experts in VRAM | 3 | complete |
| TL_coding | TL | 512 | 99.8 [94.4–100.4] | [89.0–101.0] | 308.5 | 0.33 | 6737→8791 | 0 | 8791 | 2.4 | GPU-bound: SSD path essentially unused; 2.4 Swaps/round; 8791 Experts in VRAM | 3 | complete |
| TL_math_reasoning | TL | 512 | 102.9 [97.6–104.3] | [92.3–105.8] | 347.9 | 0.33 | 6737→8791 | 0 | 8791 | 2.2 | GPU-bound: SSD path essentially unused; 2.2 Swaps/round; 8791 Experts in VRAM | 3 | complete |

## Significance (vs B1_reserve_512)

| Block | n | Median | Reference | 95% CI | p | Verdict |
|---|---:|---:|---:|---:|---:|---|
| B1 | 8 | 76.288 | 82.203 | [74.697, 78.322] | 0.2222 | no measurable difference |
| C1 | 8 | 81.454 | 82.203 | [51.965, 93.501] | 1.0000 | no measurable difference |
| D1 | 6 | 79.065 | 82.203 | [53.026, 89.665] | 1.0000 | no measurable difference |
| F1 | 15 | 81.26 | 82.203 | [78.658, 84.391] | 1.0000 | no measurable difference |
| F2 | 5 | 76.461 | 82.203 | [50.198, 84.756] | 1.0000 | no measurable difference |
| F3 | 4 | 85.934 | 82.203 | [78.069, 90.588] | 0.8000 | no measurable difference |
| G2 | 3 | 79.102 | 82.203 | [76.621, 79.482] | 0.5000 | no measurable difference |

## B2: Regression (telemetry)

| Relationship | n | r | r² | p | Slope |
|---|---:|---:|---:|---:|---:|
| experts_vs_decode | 94 | -0.037 | 0.001 | 0.7238 | -0.00144 |

## Working hypotheses

- **(a) SSD path unused (96 GB RAM):** confirmed (Median Disk read 3.9 MB/s)
- **(b) Experts in VRAM schwanken:** confirmed (spread > 500) (min 6940, max 9112)
  - Correlation with decode: r=-0.037 → no measurable relationship
- **(c) Prefill fixed cost for short prompts:** nicht confirmed (D7 Median 1141 vs. long 2043 tok/s)

## Notable observations

- 9 test(s) with warm-up > 20 s (stall after engine start): C1_auto_16384_128k (53.2 s), C1_auto_32768_128k (69.2 s), C1_auto_4096_128k (53.5 s), C1_auto_8192_128k (53.4 s), C3_decode_after_128k (54.7 s), D1_ctx_128k (53.2 s), D1_ctx_200k (87.8 s), D1_ctx_64k (31.8 s), D5_multiturn_long_128k (54.0 s)
- 6 unsuccessful runs: G3_defender, H1_power_200W, H1_power_250W, H1_power_300W, H1_power_350W, K4_vision_off
