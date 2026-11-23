# PRIVACY_CHECK

Automated check and redaction before publication.

## Redactions (first pass)

| File | Matches |
|---|---|
| `publish\configs\original-strata-iq3_s.json` | tailscale_host=1, username=5 |
| `publish\configs\recommended-strata-iq3_s.json` | tailscale_host=1, username=5 |
| `publish\DECISIONS.md` | tailscale_ip=1, username=1 |
| `publish\HANDOFF.md` | email=1 |
| `publish\results\A1_current.json` | tailscale_host=1, username=7 |
| `publish\results\A1_default.json` | tailscale_host=1, username=7 |
| `publish\results\A2_noise_end.json` | tailscale_host=1, username=5 |
| `publish\results\A2_noise_middle.json` | tailscale_host=1, username=5 |
| `publish\results\A2_noise_start.json` | tailscale_host=1, username=5 |
| `publish\results\A3_official_vs_hotrod.json` | tailscale_host=1, username=6 |
| `publish\results\B1_reserve_1024.json` | tailscale_host=1, username=5 |
| `publish\results\B1_reserve_1536.json` | tailscale_host=1, username=5 |
| `publish\results\B1_reserve_2048.json` | tailscale_host=1, username=5 |
| `publish\results\B1_reserve_256.json` | tailscale_host=1, username=5 |
| `publish\results\B1_reserve_2560.json` | tailscale_host=1, username=5 |
| `publish\results\B1_reserve_3072.json` | tailscale_host=1, username=5 |
| `publish\results\B1_reserve_4096.json` | tailscale_host=1, username=5 |
| `publish\results\B1_reserve_512.json` | tailscale_host=1, username=5 |
| `publish\results\B1_reserve_700.json` | tailscale_host=1, username=5 |
| `publish\results\B6_stability_40.json` | tailscale_host=1, username=5 |
| `publish\results\C1_auto_16384_128k.json` | tailscale_host=1, username=5 |
| `publish\results\C1_auto_16384_32k.json` | tailscale_host=1, username=5 |
| `publish\results\C1_auto_32768_128k.json` | tailscale_host=1, username=5 |
| `publish\results\C1_auto_32768_32k.json` | tailscale_host=1, username=5 |
| `publish\results\C1_auto_4096_128k.json` | tailscale_host=1, username=5 |
| `publish\results\C1_auto_4096_32k.json` | tailscale_host=1, username=5 |
| `publish\results\C1_auto_8192_128k.json` | tailscale_host=1, username=5 |
| `publish\results\C1_auto_8192_32k.json` | tailscale_host=1, username=5 |
| `publish\results\C2_auto_16384_r2048.json` | tailscale_host=1, username=5 |
| `publish\results\C2_auto_16384_r512.json` | tailscale_host=1, username=5 |
| `publish\results\C2_auto_4096_r2048.json` | tailscale_host=1, username=5 |
| `publish\results\C2_auto_4096_r512.json` | tailscale_host=1, username=5 |
| `publish\results\C3_decode_after_128k.json` | tailscale_host=1, username=5 |
| `publish\results\C3_decode_after_short.json` | tailscale_host=1, username=5 |
| `publish\results\D1_ctx_128k.json` | tailscale_host=1, username=5 |
| `publish\results\D1_ctx_16k.json` | tailscale_host=1, username=5 |
| `publish\results\D1_ctx_200k.json` | tailscale_host=1, username=5 |
| `publish\results\D1_ctx_32k.json` | tailscale_host=1, username=5 |
| `publish\results\D1_ctx_4k.json` | tailscale_host=1, username=5 |
| `publish\results\D1_ctx_64k.json` | tailscale_host=1, username=5 |
| `publish\results\D2_maxctx_131072.json` | tailscale_host=1, username=5 |
| `publish\results\D2_maxctx_262144.json` | tailscale_host=1, username=5 |
| `publish\results\D3_kv_fp16.json` | tailscale_host=1, username=5 |
| `publish\results\D3_kv_int8.json` | tailscale_host=1, username=5 |
| `publish\results\D3_kv_k8v4.json` | tailscale_host=1, username=5 |
| `publish\results\D3_kv_q4_0.json` | tailscale_host=1, username=5 |
| `publish\results\D4_output_2048.json` | tailscale_host=1, username=5 |
| `publish\results\D4_output_512.json` | tailscale_host=1, username=5 |
| `publish\results\D4_output_8192.json` | tailscale_host=1, username=5 |
| `publish\results\D5_multiturn_long_128k.json` | tailscale_host=1, username=5 |
| `publish\results\D5_multiturn_long_32k.json` | tailscale_host=1, username=5 |
| `publish\results\D5_multiturn_long_4k.json` | tailscale_host=1, username=5 |
| `publish\results\D6_convcache_0.json` | tailscale_host=1, username=5 |
| `publish\results\D6_convcache_2048.json` | tailscale_host=1, username=5 |
| `publish\results\D6_convcache_512.json` | tailscale_host=1, username=5 |
| `publish\results\D7_len_2k.json` | tailscale_host=1, username=5 |
| `publish\results\D7_len_500.json` | tailscale_host=1, username=5 |
| `publish\results\D7_len_84.json` | tailscale_host=1, username=5 |
| `publish\results\D7_len_8k.json` | tailscale_host=1, username=5 |
| `publish\results\E4_de_vs_en.json` | tailscale_host=1, username=5 |
| `publish\results\F1_expert_cache_per_layer.json` | tailscale_host=1, username=5 |
| `publish\results\F1_hc_q8_off.json` | tailscale_host=1, username=5 |
| `publish\results\F1_kv_grow.json` | tailscale_host=1, username=5 |
| `publish\results\F1_kva_off.json` | tailscale_host=1, username=5 |
| `publish\results\F1_la_learn_off.json` | tailscale_host=1, username=5 |
| `publish\results\F1_no_hit_poke.json` | tailscale_host=1, username=5 |
| `publish\results\F1_no_ple_prefetch.json` | tailscale_host=1, username=5 |
| `publish\results\F1_no_pool.json` | tailscale_host=1, username=5 |
| `publish\results\F1_ple_io_mmap.json` | tailscale_host=1, username=5 |
| `publish\results\F1_ple_io_ram.json` | tailscale_host=1, username=5 |
| `publish\results\F1_prefill_head_alias.json` | tailscale_host=1, username=5 |
| `publish\results\F1_prompt_cache_0.json` | tailscale_host=1, username=5 |
| `publish\results\F1_route_resident_off.json` | tailscale_host=1, username=5 |
| `publish\results\F1_suffix_draft_0.json` | tailscale_host=1, username=5 |
| `publish\results\F1_swap2_off.json` | tailscale_host=1, username=5 |
| `publish\results\F2_spec_2.json` | tailscale_host=1, username=5 |
| `publish\results\F2_spec_6.json` | tailscale_host=1, username=5 |
| `publish\results\F2_temp_0.json` | tailscale_host=1, username=5 |
| `publish\results\F2_temp_1.json` | tailscale_host=1, username=5 |
| `publish\results\F3_reasoning_high.json` | tailscale_host=1, username=5 |
| `publish\results\F3_reasoning_low.json` | tailscale_host=1, username=5 |
| `publish\results\F3_reasoning_medium.json` | tailscale_host=1, username=5 |
| `publish\results\F3_reasoning_none.json` | tailscale_host=1, username=5 |
| `publish\results\F4_aux_cpus_auto.json` | tailscale_host=1, username=5 |
| `publish\results\F4_host_core_last.json` | tailscale_host=1, username=5 |
| `publish\results\F4_pool_workers_4.json` | tailscale_host=1, username=5 |
| `publish\results\F4_pool_workers_8.json` | tailscale_host=1, username=5 |
| `publish\results\F5_best_combination.json` | tailscale_host=1, username=5 |
| `publish\results\G2_ram_limit_30720.json` | tailscale_host=1, username=5 |
| `publish\results\G2_ram_limit_49152.json` | tailscale_host=1, username=5 |
| `publish\results\G2_ram_limit_65536.json` | tailscale_host=1, username=5 |
| `publish\results\H2_power_plan.json` | tailscale_host=1, username=5 |
| `publish\results\I1_needle_128k.json` | tailscale_host=1, username=7 |
| `publish\results\I1_needle_32k.json` | tailscale_host=1, username=7 |
| `publish\results\I2_parity_mtp_on.json` | tailscale_host=1, username=5 |
| `publish\results\K1_vram_elastic_off.json` | tailscale_host=1, username=5 |
| `publish\results\K2_config_reserve_2048.json` | tailscale_host=1, username=5 |
| `publish\results\K6_expert_cache_off.json` | tailscale_host=1, username=5 |
| `publish\results\K7_kv_grow_long.json` | tailscale_host=1, username=5 |
| `publish\results\MINI_reserve_512.json` | tailscale_host=1, username=5 |
| `publish\results\MINI_reserve_700.json` | tailscale_host=1, username=5 |
| `publish\results\T1_record_off.json` | tailscale_host=1, username=5 |
| `publish\results\T1_record_on.json` | tailscale_host=1, username=5 |
| `publish\results\T1_recorder_off.json` | tailscale_host=1, username=5 |
| `publish\results\T1_recorder_on.json` | tailscale_host=1, username=5 |
| `publish\results\TL_chat_de.json` | tailscale_host=1, username=5 |
| `publish\results\TL_coding.json` | tailscale_host=1, username=5 |
| `publish\results\TL_math_reasoning.json` | tailscale_host=1, username=5 |
| `publish\runner\bench.py` | hostname=1, username=4, personal_path=2 |
| `publish\runner\make_matrix.py` | username=2, personal_path=2 |
| `publish\runner\matrix.yaml` | username=9, personal_path=9 |
| `publish\runner\privacy.py` | api_key=3 |
| `publish\runner\publish.py` | username=3 |
| `publish\STATE.md` | username=1, personal_path=1 |

## Remaining matches after redaction

None. Publication cleared (automated part).

## Manual checks

- [ ] No serial numbers in logs/screenshots
- [ ] No private paths in prompts/answers
- [ ] No API keys in .env files or configs
- [ ] No IP addresses in charts (axis labels)
- [ ] No personal answer text in the prompt set
