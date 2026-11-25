"""Probe alternative flag combinations for the previously failed variants.

Always restores the original config and restarts the engine in finally.
"""
from __future__ import annotations

import copy
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bench  # noqa: E402

root = Path(__file__).resolve().parent.parent
orig = bench.jload(bench.ORIGINAL_CONFIG)
comp = bench.tracker_component()


def variant(name, mutate):
    cfg = copy.deepcopy(orig)
    mutate(cfg)
    bench.write_config(cfg)
    log = bench.CONFIG_PATH.with_suffix(".log")
    off = log.stat().st_size if log.exists() else 0
    bench.stop_server(comp)
    bench.start_server(comp, cfg)
    ok, err = False, ""
    try:
        bench.wait_loaded(600)
        ok = True
    except Exception as exc:  # noqa: BLE001
        err = bench.redact(str(exc))
    tail = ""
    if log.exists():
        with log.open("r", encoding="utf-8", errors="replace") as fh:
            fh.seek(off)
            tail = fh.read()[-900:]
    print(json.dumps({"variant": name, "started": ok, "error": err,
                      "log_tail": tail[-500:]}, ensure_ascii=False), flush=True)
    return ok


def drop_flag(cfg, flag):
    args = cfg["args"]
    while flag in args:
        i = args.index(flag)
        del args[i:i + 2]


try:
    def mtp_spec2(c):
        drop_flag(c, "--mtp")
        a = c["args"]
        a[a.index("--spec") + 1] = "2"
    variant("mtp_off_keep_spec2", mtp_spec2)
    variant("mtp_off_keep_spec4", lambda c: drop_flag(c, "--mtp"))
    variant("vision_flag_only", lambda c: drop_flag(c, "--vision"))
    def vision_gpu_false(c):
        drop_flag(c, "--vision")
        if "vision" in c:
            c["vision"]["gpu"] = False
    variant("vision_flag_gpu_false", vision_gpu_false)
finally:
    bench.write_config(copy.deepcopy(orig))
    bench.stop_server(comp)
    bench.start_server(comp, copy.deepcopy(orig))
    h = bench.wait_loaded(1200)
    print(json.dumps({"restored": h.get("loaded")}, ensure_ascii=False), flush=True)
