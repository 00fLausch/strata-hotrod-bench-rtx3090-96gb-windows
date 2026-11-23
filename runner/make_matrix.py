"""Erzeugt runner/matrix.yaml — die vollstaendige, priorisierte Testmatrix."""
from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "runner" / "matrix.yaml"

PY = r"[DRIVE]/Users/[USER]\Desktop\python.toolz\apps\strata\.venv\Scripts\python.exe"
TOOLS = r"[DRIVE]/Users/[USER]\Desktop\python.toolz\apps\strata\tools"
ART = str(ROOT / "artifacts")

SHORT = ["chat_de", "chat_en", "coding", "math_reasoning"]
LONG32 = ["long_32k"]
LONG128 = ["long_128k"]

defaults = {
    "n": 8,
    "prompts": SHORT,
    # 512 MiB ist die bewaehrte Nutzer-Einstellung und ab jetzt globaler Default.
    # Nullreserve wurde verworfen (73,6 s Stall im Warm-up) und nicht weiter getestet.
    "spec": {"args": {"--vram-reserve-mib": 512}},
    "request": {"temperature": 0.6, "top_p": 0.95, "top_k": 20,
                "max_tokens": 128, "seed": 20261123, "reasoning_effort": "none"},
    "ready_timeout": 2400,
    "request_timeout": 1800,
    "retries": 1,
    "telemetry": True,
    "telemetry_rate": 1.0,
    "record_timeline": False,
}

tests = []


def add(tid, block, priority, label, **kw):
    t = {"id": tid, "block": block, "priority": priority, "label": label}
    t.update(kw)
    tests.append(t)


# ---------------------------------------------------------------- Prioritaet 1
add("A1_default", "A1", 1, "strata bench run, Default-Config",
    kind="command",
    command=[PY, str(Path(TOOLS) / "strata_bench.py"), "--url", "http://127.0.0.1:8080",
             "--out", str(Path(ART) / "a1-default")],
    spec={"env": {"STRATA_LA_LEARN": "0", "STRATA_HC_Q8": "0", "STRATA_KVA": "0",
                  "STRATA_ROUTE_RESIDENT": "0", "STRATA_SWAP2_MAX": "0"}},
    timeout=3600)
add("A1_current", "A1", 1, "strata bench run, aktuelle Config",
    kind="command",
    command=[PY, str(Path(TOOLS) / "strata_bench.py"), "--url", "http://127.0.0.1:8080",
             "--out", str(Path(ART) / "a1-current")],
    timeout=3600)

# A2: absichtlich NICHT innerhalb des Blocks mischen (Start/Mitte/Ende).
for suffix, block in (("start", "A2_1"), ("middle", "A2_2"), ("end", "A2_3")):
    add(f"A2_noise_{suffix}", block, 1, f"Rauschmessung {suffix}",
        prompts=["chat_de", "coding"], n=8)

# T1: Telemetrie-Overhead (Recorder aus/an) und Record-Overhead (Timeline aus/an).
add("T1_recorder_off", "T1_1", 1, "Telemetrie-Recorder AUS (Baseline)",
    telemetry=False, prompts=SHORT, n=8)
add("T1_recorder_on", "T1_2", 1, "Telemetrie-Recorder AN (1 Hz)",
    telemetry=True, prompts=SHORT, n=8)
add("T1_record_off", "T1_3", 1, "Timeline-Record AUS",
    record_timeline=False, prompts=SHORT, n=8)
add("T1_record_on", "T1_4", 1, "Timeline-Record AN",
    record_timeline=True, prompts=SHORT, n=8)

for reserve in (256, 512, 700, 1024, 1536, 2048, 2560, 3072, 4096):
    # 512 zuerst (bewaehrte Nutzer-Einstellung), Rest randomisiert.
    block = "B1_0" if reserve == 512 else "B1"
    add(f"B1_reserve_{reserve}", block, 1, f"vram-reserve-mib {reserve}",
        spec={"args": {"--vram-reserve-mib": reserve}}, prompts=SHORT, n=8)

for prefill in ("auto:4096", "auto:8192", "auto:16384", "auto:32768"):
    tag = prefill.replace(":", "_")
    add(f"C1_{tag}_32k", "C1", 1, f"prefill {prefill}, 32K-Prompt",
        spec={"args": {"--prefill": prefill}}, prompts=LONG32, n=8,
        request={"temperature": 0.6, "max_tokens": 16, "reasoning_effort": "none"})
    add(f"C1_{tag}_128k", "C1", 1, f"prefill {prefill}, 128K-Prompt",
        spec={"args": {"--prefill": prefill}}, prompts=LONG128, n=5,
        request={"temperature": 0.6, "max_tokens": 16, "reasoning_effort": "none"},
        request_timeout=3600)

# D7: ab wann verschwinden die Prefill-Fixkosten?
for plen, pid in (("84", "chat_de"), ("500", "len_500"), ("2k", "len_2k"), ("8k", "len_8k")):
    add(f"D7_len_{plen}", "D7", 1, f"Prompt-Länge {plen} Tokens",
        prompts=[pid], n=8,
        request={"temperature": 0.6, "max_tokens": 96, "reasoning_effort": "none"})

for ctx, pid in (("4k", "long_4k"), ("16k", "long_16k"), ("32k", "long_32k"),
                 ("64k", "long_64k"), ("128k", "long_128k")):
    add(f"D1_ctx_{ctx}", "D1", 1, f"Kontext-Sweep {ctx}",
        prompts=[pid], n=8,
        request={"temperature": 0.6, "max_tokens": 16, "reasoning_effort": "none"},
        request_timeout=3600)
add("D1_ctx_200k", "D1", 1, "Kontext-Sweep 200K (262144-max-context)",
    spec={"args": {"--max-context": 262144}}, prompts=["long_200k"], n=3,
    request={"temperature": 0.6, "max_tokens": 16, "reasoning_effort": "none"},
    request_timeout=5400, ready_timeout=3600)

# ---------------------------------------------------------------- Prioritaet 2
add("E1_learn_from_empty", "E1", 2, "Lernkurve ab leeren Lerndaten (150 Requests)",
    kind="learning", clear_learning=True, n=150, prompts=["chat_de", "coding"])
add("E3_train_coding_measure_chat", "E3", 2, "Coding einlernen, Chat messen",
    kind="learning", clear_learning=True, n=80, prompts=["chat_de", "chat_en"],
    warmup_id="coding")
add("E3_train_chat_measure_coding", "E3", 2, "Chat einlernen, Coding messen",
    kind="learning", clear_learning=True, n=80, prompts=["coding"],
    warmup_id="chat_de")
add("E4_de_vs_en", "E4", 2, "Deutsch vs. Englisch, identische Aufgabe",
    prompts=["chat_de", "chat_en"], n=8)

# F1: nur tatsaechlich existierende Schalter (engine --help / Config / Doku).
f1 = {
    "F1_la_learn_off": ("Look-ahead-Lernen aus", {"env": {"STRATA_LA_LEARN": "0"}}),
    "F1_hc_q8_off": ("Hyperconnection Q8 aus", {"env": {"STRATA_HC_Q8": "0"}}),
    "F1_kva_off": ("STRATA_KVA aus", {"env": {"STRATA_KVA": "0"}}),
    "F1_route_resident_off": ("Route-Resident aus", {"env": {"STRATA_ROUTE_RESIDENT": "0"}}),
    "F1_swap2_off": ("SWAP2 aus", {"env": {"STRATA_SWAP2_MAX": "0"}}),
    "F1_no_ple_prefetch": ("PLE-Prefetch aus", {"args": {"--no-ple-prefetch": None}}),
    "F1_no_hit_poke": ("Hit-Poke aus", {"args": {"--no-hit-poke": None}}),
    "F1_expert_cache_per_layer": ("Expert-Cache per Layer", {"args": {"--expert-cache-per-layer": None}}),
    "F1_ple_io_mmap": ("PLE-IO mmap", {"args": {"--ple-io": "mmap"}}),
    "F1_ple_io_ram": ("PLE-IO ram", {"args": {"--ple-io": "ram"}}),
    "F1_no_pool": ("CPU-Expert-Pool aus", {"args": {"--no-pool": None}}),
    "F1_kv_grow": ("KV-Grow an", {"args": {"--kv-grow": None}}),
    "F1_suffix_draft_0": ("Suffix-Draft aus", {"args": {"--suffix-draft": 0}}),
    "F1_prompt_cache_0": ("Prompt-Cache aus", {"args": {"--prompt-cache": 0}}),
    "F1_prefill_head_alias": ("Prefill-Head-Alias an", {"args": {"--prefill-head-alias": None}}),
}
for tid, (label, spec) in f1.items():
    add(tid, "F1", 2, label, spec=spec, prompts=SHORT, n=8)

f2 = {
    "F2_mtp_off": ("MTP/Speculative aus", {"args": {"--mtp": None, "--spec": None, "--spec-min-p": None}}),
    "F2_spec_2": ("Spec-Verification 2", {"args": {"--spec": 2}}),
    "F2_spec_6": ("Spec-Verification 6", {"args": {"--spec": 6}}),
    "F2_temp_0": ("Temperatur 0", {}, {"temperature": 0.0}),
    "F2_temp_1": ("Temperatur 1.0", {}, {"temperature": 1.0}),
}
for tid, (label, spec, *req) in f2.items():
    add(tid, "F2", 2, label, spec=spec, prompts=SHORT, n=8,
        request={"temperature": req[0]["temperature"]} if req else None)

for gib in (65536, 49152, 30720):
    add(f"G2_ram_limit_{gib}", "G2", 2, f"RAM-Tier {gib // 1024} GiB",
        spec={"args": {"--memory-limit-mib": gib}}, prompts=SHORT, n=5)

# D6: Conversation Cache (Mehrturn-Szenario, wiederverwendete Tokens aus Telemetrie).
for mib in (0, 512, 2048):
    add(f"D6_convcache_{mib}", "D6", 2, f"Conversation-Cache {mib} MiB",
        spec={"args": {"--conversation-cache-mib": mib}},
        prompts=["chat_de"], n=8, warmup_id="long_4k")

# Decode-Timeline: separate Läufe mit Record AN (Speed-Läufe bleiben ohne Record).
for pid in ("chat_de", "coding", "math_reasoning"):
    add(f"TL_{pid}", "TL", 2, f"Decode-Timeline Record: {pid}",
        record_timeline=True, prompts=[pid], n=3,
        request={"max_tokens": 256}, request_timeout=1200)

for length in ("32k", "128k"):
    add(f"I1_needle_{length}", "I1", 2, f"Needle-Recall {length}",
        kind="command",
        command=[PY, str(Path(TOOLS) / "needle_bench.py"), "--url", "http://127.0.0.1:8080",
                 "--lengths", length, "--depths", "10,50,90",
                 "--out", str(Path(ART) / f"needles-{length}.json")],
        timeout=5400, ready_timeout=2400)

# ---------------------------------------------------------------- Prioritaet 3
add("B6_stability_40", "B6", 3, "Stabilitaet ueber 40 Requests", prompts=SHORT, n=10)
for prefill in ("auto:4096", "auto:16384"):
    for reserve in (512, 2048):
        add(f"C2_{prefill.replace(':', '_')}_r{reserve}", "C2", 3,
            f"Wechselwirkung {prefill} x Reserve {reserve}",
            spec={"args": {"--prefill": prefill, "--vram-reserve-mib": reserve}},
            prompts=LONG32, n=5, request={"max_tokens": 16})

add("C3_decode_after_128k", "C3", 3, "Decode direkt nach 128K-Prefill",
    prompts=["chat_de"], n=5, warmup_id="long_128k", request_timeout=3600)
add("C3_decode_after_short", "C3", 3, "Decode nach kurzem Prompt",
    prompts=["chat_de"], n=5, warmup_id="chat_de")

for ctx in (131072, 262144):
    add(f"D2_maxctx_{ctx}", "D2", 3, f"--max-context {ctx} bei kurzen Prompts",
        spec={"args": {"--max-context": ctx}}, prompts=SHORT, n=5,
        ready_timeout=3600 if ctx > 131072 else 2400)

for kv in ("fp16", "int8", "q4_0", "k8v4"):
    add(f"D3_kv_{kv}", "D3", 3, f"KV-Cache-Variante {kv}",
        spec={"args": {"--kv": kv}}, prompts=SHORT + ["long_4k"], n=5)

for tok in (512, 2048, 8192):
    add(f"D4_output_{tok}", "D4", 3, f"Lange Ausgabe {tok} Tokens",
        prompts=["chat_de"], n=5,
        request={"max_tokens": tok, "temperature": 0.6}, request_timeout=3600)

for hist in ("long_4k", "long_32k", "long_128k"):
    add(f"D5_multiturn_{hist}", "D5", 3, f"Mehrturn-Verlauf {hist}",
        prompts=["chat_de"], n=5, warmup_id=hist, request_timeout=3600)

add("E5_persist_after_restart", "E5", 3, "Persistenz des Gelernten nach Neustart",
    kind="learning", clear_learning=False, n=40, prompts=["chat_de"])

for effort in ("none", "low", "medium", "high"):
    add(f"F3_reasoning_{effort}", "F3", 3, f"Reasoning-Budget {effort}",
        prompts=SHORT, n=5, request={"reasoning_effort": effort, "max_tokens": 256},
        request_timeout=3600)

for tid, label, spec in (
    ("F4_host_core_last", "Host-Core last", {"args": {"--host-core": "last"}}),
    ("F4_aux_cpus_auto", "Aux-CPUs auto", {"args": {"--aux-cpus": "auto"}}),
    ("F4_pool_workers_4", "Pool-Workers 4", {"args": {"--pool-workers": 4}}),
    ("F4_pool_workers_8", "Pool-Workers 8", {"args": {"--pool-workers": 8}}),
):
    add(tid, "F4", 3, label, spec=spec, prompts=SHORT, n=5)

add("F5_best_combination", "F5", 3, "Kombination der besten Einzel-Schalter",
    spec={"args": {"--prefill": "auto:8192", "--vram-reserve-mib": 2048},
          "env": {"STRATA_LA_LEARN": "1"}}, prompts=SHORT, n=8)

for watts in (350, 300, 250, 200):
    add(f"H1_power_{watts}W", "H1", 3, f"Power-Limit {watts} W",
        kind="power", spec={"watts": watts}, prompts=SHORT, n=5)

for tid, label, spec in (
    ("I2_parity_mtp_on", "Output-Paritaet MTP an", {}),
    ("I2_parity_mtp_off", "Output-Paritaet MTP aus",
     {"args": {"--mtp": None, "--spec": None, "--spec-min-p": None}}),
):
    add(tid, "I2", 3, label, spec=spec, prompts=["chat_de", "math_reasoning"], n=5,
        request={"temperature": 0.0, "seed": 20261123})

add("J1_parallel_1", "J1", 4, "1 paralleler Request", kind="concurrent", parallel=1, n=5)
add("J1_parallel_2", "J1", 4, "2 parallele Requests", kind="concurrent", parallel=2, n=5)
add("J1_parallel_4", "J1", 4, "4 parallele Requests", kind="concurrent", parallel=4, n=5)
add("J2_soak_90min", "J2", 4, "Dauertest 90 min", kind="soak", duration_s=5400)
add("J3_oversized", "J3", 4, "Zu grosser Prompt", kind="error", mode="oversized")
add("J3_abort_prefill", "J3", 4, "Abbruch mitten im Prefill", kind="error", mode="abort")

# K — Agent-Vorschlaege, einzigartig fuer Windows + 24 GB VRAM + 96 GB RAM.
add("K1_vram_elastic_off", "K", 3, "[Agent-Vorschlag] --vram-elastic aus",
    spec={"args": {"--vram-elastic": None}}, prompts=SHORT, n=5)
add("K2_config_reserve_2048", "K", 3, "[Agent-Vorschlag] Config-Reserve 2048 (statt 1792)",
    spec={"config_keys": {"vram_reserve_mib": 2048}}, prompts=SHORT, n=5)
add("K4_vision_off", "K", 3, "[Agent-Vorschlag] Vision aus (VRAM-Rueckgewinn)",
    spec={"args": {"--vision": None}, "config_keys": {"ui_vision_enabled": False}},
    prompts=SHORT, n=5)
add("K6_expert_cache_off", "K", 3, "[Agent-Vorschlag] Expert-Cache aus",
    spec={"args": {"--expert-cache": None}}, prompts=SHORT, n=5)
add("K7_kv_grow_long", "K", 3, "[Agent-Vorschlag] KV-Grow bei 32K",
    spec={"args": {"--kv-grow": None}}, prompts=LONG32, n=5,
    request={"max_tokens": 16})

# ---------------------------------------------------------------- Prioritaet 4 (ueberwiegend manuell)
add("A3_official_vs_hotrod", "A3", 4, "Offizielles Strata vs. HotRod",
    kind="command",
    command=[PY, "-c", "print('SKIP: offizielle Strata-Engine nicht mit diesem Modell/Pack konfiguriert; manuell moeglich')"],
    timeout=120)
add("G3_defender", "G4", 4, "Defender-Ausnahme an/aus",
    kind="defender", spec={"path": r"D:\Strata-HotRod-data"},
    prompts=SHORT, n=5)
add("H2_power_plan", "H2", 4, "Energieplan Hoechstleistung",
    kind="plan", spec={"guid": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"},
    prompts=SHORT, n=5)

payload = {
    "version": "1.0",
    "created": "2026-11-23",
    "seed": 20261123,
    "note": "Blocke in Prioritaetsreihenfolge; innerhalb eines Blocks randomisiert. A2 absichtlich geordnet.",
    "defaults": defaults,
    "tests": tests,
}
OUT.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False,
                              default_flow_style=False), encoding="utf-8")
h = hashlib.sha256(OUT.read_bytes()).hexdigest()
OUT.with_suffix(".yaml.sha256").write_text(h + "\n", encoding="ascii")
from collections import Counter
by_p = Counter(t["priority"] for t in tests)
print(f"wrote {OUT} with {len(tests)} tests, priorities={dict(by_p)}, sha256={h}")
