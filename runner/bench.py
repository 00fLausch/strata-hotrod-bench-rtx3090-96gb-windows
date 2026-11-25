"""Autonomer Benchmark-Runner fuer Strata-HotRod (Windows, RTX 3090, 96 GB RAM).

Abarbeitung einer YAML-Matrix. Pro Test ein JSON unter results/<test_id>.json.
Resume: abgeschlossene Tests werden uebersprungen.
Config-, Power-Limit-, Energieplan-, Defender- und Lerndaten-Wiederherstellung
laufen immer in try/finally. TEMP/TMP zeigt auf D:\\strata-bench\\tmp.

Keine Verwendung des lokalen Strata-Modells als eigenes Sprachmodell dieses Agenten.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import random
import re
import shutil
import signal
import statistics
import subprocess
import sys
import threading
import time
import traceback
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

import numpy as np
import psutil
import tempfile
import yaml

from telemetry import TelemetryRecorder, record_status, set_record
from concurrent.futures import ThreadPoolExecutor
from scipy import stats as scipy_stats

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
LOGS = ROOT / "logs"
TMP = ROOT / "tmp"
CONFIGS = ROOT / "configs"
PROMPTS = ROOT / "prompts" / "prompts.json"

STRATA_DIR = Path(r"[DRIVE]/Users/[USER]\Desktop\python.toolz\apps\strata")
CONFIG_PATH = STRATA_DIR / "strata-iq3_s.json"
ORIGINAL_CONFIG = CONFIGS / "original-strata-iq3_s.json"
TRACKER_DIR = Path(r"[DRIVE]/Users/[USER]\Desktop\python.toolz\apps\python-tracker")
TRACKER_CONFIG = TRACKER_DIR / "config.json"

SEED = 20261123
BASE_URL = "http://127.0.0.1:8080"

AUTO_RE = re.compile(r"expert cache auto: ([\d.]+) GiB free, (\d+) MiB reserved.*?-> (\d+) slots")
SHRINK_RE = re.compile(r"only (\d+) MiB free once the slots are written \(reserve (\d+) MiB\); shrinking")
CACHE_RE = re.compile(r"expert cache (\d+) slots, ([\d.]+) GiB of VRAM")
LOADED_RE = re.compile(r"(\d+) MiB of VRAM free with everything loaded")
CHUNK_RE = re.compile(r"prompt chunk (\d+)")
SERVE_RE = re.compile(r"the expert cache \d+ -> \d+ of (\d+) slots \(([\d.]+) of ([\d.]+) GiB\)")

LEARN_FILES = [
    STRATA_DIR / "data" / "predictor-905fc7359fc3c491.bin",
    STRATA_DIR / "data" / "standin-tune-905fc7359fc3c491.txt",
]

_state = {"stop": False}


def log(msg: str) -> None:
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line, flush=True)
    with (LOGS / "runner.log").open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def jdump(obj, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def jload(path: Path):
    return json.loads(path.read_text("utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def http_json(url: str, body=None, timeout: int = 120):
    headers = {"Content-Type": "application/json", "Origin": BASE_URL}
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8") if body is not None else None,
        headers=headers,
        method="POST" if body is not None else "GET",
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(req, timeout=timeout) as resp:
        return json.load(resp)


def chat_stream(body: dict, timeout: int = 1800) -> dict:
    """SSE-Streaming: TTFT clientseitig, Engine-Timings aus dem letztenChunk."""
    import requests

    url = BASE_URL + "/v1/chat/completions"
    t0 = time.monotonic()
    out = {
        "ttft_s": None,
        "wall_s": None,
        "content": "",
        "reasoning": "",
        "finish": None,
        "timings": None,
        "usage": None,
        "error": None,
        "first_token_kind": None,
        "n_chunks": 0,
    }
    try:
        with requests.post(url, json=body, stream=True,
                           timeout=(30, timeout),
                           headers={"Origin": BASE_URL}) as resp:
            if resp.status_code >= 400:
                out["error"] = f"HTTP {resp.status_code}: {resp.text[:500]}"
                out["wall_s"] = round(time.monotonic() - t0, 3)
                return out
            for raw in resp.iter_lines(decode_unicode=True):
                if not raw or not raw.startswith("data:"):
                    continue
                data = raw[5:].strip()
                if data == "[DONE]":
                    break
                if not data:
                    continue
                try:
                    item = json.loads(data)
                except ValueError:
                    continue
                out["n_chunks"] += 1
                if item.get("timings"):
                    out["timings"] = item["timings"]
                if item.get("usage"):
                    out["usage"] = item["usage"]
                choices = item.get("choices") or []
                if choices:
                    ch = choices[0]
                    d = ch.get("delta") or {}
                    msg = ch.get("message") or {}
                    piece = d.get("content") or msg.get("content") or ""
                    reason = d.get("reasoning_content") or d.get("reasoning") or ""
                    if out["ttft_s"] is None and (piece or reason):
                        out["ttft_s"] = round(time.monotonic() - t0, 3)
                        out["first_token_kind"] = "reasoning" if reason and not piece else "answer"
                    out["content"] += piece or ""
                    out["reasoning"] += reason or ""
                    if ch.get("finish_reason"):
                        out["finish"] = ch["finish_reason"]
    except Exception as exc:  # noqa: BLE001
        out["error"] = redact(str(exc))
    out["wall_s"] = round(time.monotonic() - t0, 3)
    return out


def redact(text: str) -> str:
    if not text:
        return text
    text = re.sub(r"100\.\d+\.\d+\.\d+", "[tailscale-ip]", text)
    text = re.sub(r"\b(?:192\.168|10\.|172\.(?:1[6-9]|2\d|3[01]))\d*\.\d+\.\d+", "[local-ip]", text)
    text = re.sub(r"[\w.+-]+@[\w.-]+\.\w+", "[email]", text)
    text = text.replace("[USER]", "[user]").replace("[HOSTNAME]", "[host]")
    return text


# ---------------------------------------------------------------- engine control

def tracker_component() -> dict:
    cfg = jload(TRACKER_CONFIG)
    for app in cfg["apps"]:
        if app.get("id") == "strata":
            for comp in app.get("components", []):
                if comp.get("id") == "server":
                    return comp
    raise RuntimeError("Strata-Serverkomponente im Tracker nicht gefunden")


def server_processes() -> list[psutil.Process]:
    needle = "--config " + str(CONFIG_PATH)
    found = []
    for proc in psutil.process_iter(["pid", "cmdline", "exe", "create_time"]):
        try:
            cmd = " ".join(proc.info["cmdline"] or [])
            if "serve.server" in cmd and needle in cmd and "python" in (proc.info["exe"] or "").lower():
                found.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return found


def stop_server(component: dict, timeout: int = 180) -> None:
    try:
        subprocess.run(component["stop_command"], cwd=component["cwd"], timeout=timeout,
                       check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       env={**os.environ, "TEMP": str(TMP), "TMP": str(TMP)})
    except Exception as exc:  # noqa: BLE001
        log(f"stop_command Warnung: {redact(str(exc))}")
    procs = server_processes()
    targets = []
    for proc in procs:
        try:
            targets.extend(proc.children(recursive=True))
        except psutil.NoSuchProcess:
            pass
        targets.append(proc)
    # Auch die Engine selbst (Kind des Servers) kann uebrig bleiben.
    for proc in psutil.process_iter(["pid", "exe", "cmdline"]):
        try:
            exe = proc.info["exe"] or ""
            if exe and os.path.basename(exe).lower() == "strata.exe" and "--serve" in " ".join(proc.info["cmdline"] or []):
                if proc not in targets:
                    targets.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    for proc in targets:
        try:
            proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    deadline = time.monotonic() + 90
    for proc in targets:
        try:
            proc.wait(timeout=max(0, deadline - time.monotonic()))
        except (psutil.TimeoutExpired, psutil.NoSuchProcess, psutil.AccessDenied):
            try:
                proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    time.sleep(2)


def start_server(component: dict, cfg: dict) -> None:
    env = {**os.environ, **component.get("env", {}), "TEMP": str(TMP), "TMP": str(TMP),
           "TMPDIR": str(TMP)}
    subprocess.Popen(component["command"], cwd=component["cwd"], env=env,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)


def wait_loaded(timeout: int = 2400) -> dict:
    deadline = time.monotonic() + timeout
    last = None
    no_proc_since = None
    while time.monotonic() < deadline:
        if _state["stop"]:
            raise KeyboardInterrupt("run interrupted")
        # Fail-fast: wenn der Engine-Prozess fehlt, wartet niemand mehr auf Load.
        if not server_processes():
            if no_proc_since is None:
                no_proc_since = time.monotonic()
            elif time.monotonic() - no_proc_since > 90:
                raise TimeoutError("Engine-Prozess beendet sich sofort (ungueltige Flags) — kein Load zu erwarten")
        else:
            no_proc_since = None
        try:
            h = http_json(BASE_URL + "/health", timeout=10)
            if h.get("loaded"):
                return h
            last = h
        except (urllib.error.URLError, OSError, ValueError, TimeoutError):
            pass
        time.sleep(3)
    raise TimeoutError(f"Modell nicht geladen nach {timeout}s (letzte Health: {last})")


def apply_config(base: dict, spec: dict) -> dict:
    cfg = copy.deepcopy(base)
    args = list(cfg.get("args", []))
    for flag, value in (spec.get("args") or {}).items():
        if value is None:
            while flag in args:
                i = args.index(flag)
                del args[i:i + 2]
        else:
            if flag in args:
                args[args.index(flag) + 1] = str(value)
            else:
                args.extend([flag, str(value)])
    cfg["args"] = args
    for key, value in (spec.get("config_keys") or {}).items():
        cfg[key] = value
    env = dict(cfg.get("env") or {})
    env.update({k: str(v) for k, v in (spec.get("env") or {}).items()})
    cfg["env"] = env
    return cfg


def write_config(cfg: dict) -> None:
    """Atomar schreiben; Windows kann die Zieldatei kurz nach einem Engine-Start sperren."""
    tmp = CONFIG_PATH.with_name(CONFIG_PATH.name + ".bench-tmp")
    payload = json.dumps(cfg, ensure_ascii=False, indent=2) + "\n"
    last = None
    for attempt in range(10):
        try:
            tmp.write_text(payload, encoding="utf-8")
            os.replace(tmp, CONFIG_PATH)
            return
        except (PermissionError, OSError) as exc:
            last = exc
            time.sleep(0.5 * (attempt + 1))
    if last:
        raise last


def parse_startup(log_path: Path, offset: int) -> dict:
    with log_path.open("r", encoding="utf-8", errors="replace") as fh:
        fh.seek(offset)
        text = fh.read()
    auto = AUTO_RE.search(text)
    cache = CACHE_RE.search(text)
    serve = SERVE_RE.search(text)
    loaded = LOADED_RE.search(text)
    chunk = CHUNK_RE.search(text)
    return {
        "auto_free_gib": float(auto.group(1)) if auto else None,
        "auto_reserve_mib": int(auto.group(2)) if auto else None,
        "auto_slots": int(auto.group(3)) if auto else None,
        "shrink_rounds": len(SHRINK_RE.findall(text)),
        "final_slots": int(cache.group(1)) if cache else int(serve.group(1)) if serve else None,
        "final_gib": float(cache.group(2)) if cache else float(serve.group(2)) if serve else None,
        "free_mib_after_load": int(loaded.group(1)) if loaded else None,
        "prompt_chunk": int(chunk.group(1)) if chunk else None,
        "startup_lines": len(text.splitlines()),
    }


def collect_engine_facts() -> dict:
    """Nur kleine, gefilterte Fakten aus /metrics (/metrics selbst ist gross)."""
    try:
        raw = http_json(BASE_URL + "/metrics", timeout=30)
    except Exception:  # noqa: BLE001
        return {}
    eng = raw.get("engine", {})
    hw = raw.get("hardware", {})
    return {
        "expert_slots": eng.get("expert_slots"),
        "expert_cache_mib": eng.get("expert_cache_mib"),
        "expert_slots_primary": eng.get("expert_slots_primary"),
        "vram_free_mib": eng.get("vram_free_mib"),
        "arena_mib": eng.get("arena_mib"),
        "kv": eng.get("kv"),
        "kv_resident": eng.get("kv_resident"),
        "prefill_cap": eng.get("prefill_cap"),
        "spec": eng.get("spec"),
        "spec_min_p": eng.get("spec_min_p"),
        "vram_elastic": eng.get("vram_elastic"),
        "pool_workers": eng.get("pool_workers"),
        "pcie_gen": hw.get("gpu_pcie_gen"),
        "pcie_width": hw.get("gpu_pcie_gen_max"),
        "disk_read_mb": hw.get("disk_read_mb"),
        "disk_write_mb": hw.get("disk_write_mb"),
        "ram_used": hw.get("ram_used"),
        "ram_total": hw.get("ram_total"),
        "gpu_temp": hw.get("gpu_temp"),
        "gpu_power": hw.get("gpu_power"),
    }


class Sampler(threading.Thread):
    """1-Hz-GPU-/CPU-/RAM-Sampler waehrend eines Tests."""

    def __init__(self):
        super().__init__(daemon=True)
        self.samples: list[dict] = []
        self.running = True
        # Kein NVML im Konstruktor: nvidia-smi/pynvml koennen nach dem Beenden
        # eines GPU-Prozesses unter WDDM blockieren. /v1/status des Engines
        # liefert diesbezoeglich zuverlaessige, leichtgewichtige Werte.

    def run(self):
        while self.running:
            sample = {"t": time.time()}
            try:
                st = http_json(BASE_URL + "/v1/status", timeout=10)
                machine = st.get("machine") or {}
                gpu = machine.get("gpu") or {}
                sample["power_w"] = gpu.get("power_w")
                sample["temp_c"] = gpu.get("temp_c")
                sample["util_pct"] = gpu.get("util_pct")
                sample["mem_used_mib"] = round(gpu["used_mib"] / 1048576, 1) if gpu.get("used_mib") else None
                ram = machine.get("ram") or {}
                sample["ram_used_gib"] = round(ram["used_gib"], 2) if ram.get("used_gib") else None
            except Exception:  # noqa: BLE001
                pass
            sample["ram_pct"] = psutil.virtual_memory().percent
            sample["cpu_pct"] = psutil.cpu_percent(interval=None)
            self.samples.append(sample)
            time.sleep(2)

    def stop(self) -> dict:
        self.running = False
        self.join(timeout=3)
        if not self.samples:
            return {}
        def nums(key):
            return [s[key] for s in self.samples if isinstance(s.get(key), (int, float))]
        out = {"n_samples": len(self.samples)}
        for key in ("power_w", "temp_c", "mem_used_mib", "util_pct", "ram_pct", "cpu_pct", "ram_used_gib"):
            vals = nums(key)
            if vals:
                out[f"{key}_mean"] = round(float(np.mean(vals)), 2)
                out[f"{key}_max"] = round(float(np.max(vals)), 2)
        return out


# ---------------------------------------------------------------- statistics

def describe(values: list[float]) -> dict:
    vals = [float(v) for v in values if isinstance(v, (int, float)) and np.isfinite(v)]
    if not vals:
        return {"n": 0}
    arr = np.array(vals)
    q1, q3 = np.percentile(arr, [25, 75])
    rng = np.random.default_rng(SEED)
    boots = np.median(rng.choice(arr, size=(10000, len(arr)), replace=True), axis=1)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {
        "n": len(vals),
        "median": round(float(np.median(arr)), 4),
        "q1": round(float(q1), 4),
        "q3": round(float(q3), 4),
        "iqr": round(float(q3 - q1), 4),
        "min": round(float(np.min(arr)), 4),
        "max": round(float(np.max(arr)), 4),
        "ci95_low": round(float(lo), 4),
        "ci95_high": round(float(hi), 4),
        "mean": round(float(np.mean(arr)), 4),
    }


def compare(a: list[float], b: list[float]) -> dict:
    if len(a) < 3 or len(b) < 3:
        return {"verdict": "zu wenig Daten", "p": None}
    try:
        u, p = scipy_stats.mannwhitneyu(a, b, alternative="two-sided")
    except ValueError:
        u, p = None, None
    da, db = describe(a), describe(b)
    overlap = not (da["ci95_high"] < db["ci95_low"] or db["ci95_high"] < da["ci95_low"])
    if not overlap:
        verdict = "signifikant (KI ueberlappen nicht)"
    elif p is not None and p < 0.05:
        verdict = "signifikant (Mann-Whitney p<0.05)"
    else:
        verdict = "kein messbarer Unterschied"
    return {"verdict": verdict, "p": round(float(p), 6) if p is not None else None,
            "u": float(u) if u is not None else None, "a": da, "b": db}


# ---------------------------------------------------------------- capabilities

def probe_capabilities() -> dict:
    caps = {}
    # Primär: Engine-Metriken (NVML-basiert, aber im Engine-Prozess bereits initialisiert).
    facts = collect_engine_facts()
    st = {}
    try:
        st = http_json(BASE_URL + "/v1/status", timeout=10)
    except Exception:  # noqa: BLE001
        pass
    metrics_limit = None
    try:
        raw = http_json(BASE_URL + "/metrics", timeout=20)
        metrics_limit = (raw.get("hardware") or {}).get("gpu_power_limit")
    except Exception:  # noqa: BLE001
        pass
    caps["power_limit_w_original"] = metrics_limit
    caps["power_source"] = "engine /metrics"
    # nvidia-smi nur mit hartem Timeout testen; haengt unter WDDM nach GPU-Prozess-Wechsel.
    try:
        r = subprocess.run(["nvidia-smi", "-pl", str(int(metrics_limit or 350))],
                           capture_output=True, text=True, timeout=15)
        caps["power_limit_change_possible"] = r.returncode == 0
        if r.returncode != 0:
            caps["power_limit_error"] = redact(r.stderr.strip()[:300])
    except subprocess.TimeoutExpired:
        caps["power_limit_change_possible"] = False
        caps["power_limit_error"] = "nvidia-smi haengt (NVML/WDDM) — Power-Limit nicht automatisierbar"
    except Exception as exc:  # noqa: BLE001
        caps["power_limit_change_possible"] = False
        caps["power_limit_error"] = redact(str(exc))
    caps["engine_status_ok"] = bool(st.get("loaded"))
    try:
        out = subprocess.run(["powercfg", "/getactivescheme"], capture_output=True,
                             text=True, timeout=30).stdout
        m = re.search(r"([0-9a-fA-F-]{36})", out)
        caps["power_plan_original"] = m.group(1) if m else None
        caps["power_plan_original_name"] = out.strip()
    except Exception as exc:  # noqa: BLE001
        caps["power_plan_original"] = None
        caps["power_plan_error"] = redact(str(exc))
    caps["defender_exclusion_possible"] = None  # wird bei Bedarf geprueft
    jdump(caps, ROOT / "CAPABILITIES.json")
    log(f"Capabilities: {json.dumps(caps, ensure_ascii=False)}")
    return caps


def set_power_limit(watts: float | None) -> bool:
    if watts is None:
        return False
    try:
        r = subprocess.run(["nvidia-smi", "-pl", str(int(watts))], capture_output=True,
                           text=True, timeout=15)
        log(f"Power-Limit -> {watts} W: rc={r.returncode} {redact(r.stderr.strip()[:200])}")
        return r.returncode == 0
    except subprocess.TimeoutExpired:
        log(f"Power-Limit {watts} W: nvidia-smi haengt — nicht automatisierbar")
        return False
    except Exception as exc:  # noqa: BLE001
        log(f"Power-Limit Fehler: {redact(str(exc))}")
        return False


# ---------------------------------------------------------------- test execution

def load_prompts() -> dict:
    payload = jload(PROMPTS)
    return {p["id"]: p for p in payload["prompts"]}


def make_body(prompt: dict, test: dict, rep: int) -> dict:
    req = test.get("request") or {}
    seed_base = int(req.get("seed", SEED))
    max_tokens = int(req.get("max_tokens", 128 if prompt["kind"] == "short" else 16))
    body = {
        "model": "qwen3.8-flash-next-iq3_s",
        "messages": [
            {"role": "system", "content": req.get("system", "Antworte direkt und vollstaendig ohne Werkzeuge.")},
            {"role": "user", "content": prompt["text"]},
        ],
        "temperature": float(req.get("temperature", 0.6)),
        "top_p": float(req.get("top_p", 0.95)),
        "top_k": int(req.get("top_k", 20)),
        "seed": seed_base + rep,
        "max_tokens": max_tokens,
        "reasoning_effort": req.get("reasoning_effort", "none"),
        "stream": True,
        "strata_checkpoint": False,
    }
    return body


def run_http_test(test: dict, base: dict, component: dict, caps: dict) -> dict:
    cfg = apply_config(base, test.get("spec") or {})
    write_config(cfg)
    log_path = CONFIG_PATH.with_suffix(".log")
    offset = log_path.stat().st_size if log_path.exists() else 0
    stop_server(component)
    start_server(component, cfg)
    health = wait_loaded(int(test.get("ready_timeout", 2400)))
    startup = parse_startup(log_path, offset)
    facts0 = collect_engine_facts()
    prompts = load_prompts()
    ids = test.get("prompts") or ["chat_de"]
    n = int(test.get("n", 8))
    records = []
    sampler = Sampler()
    sampler.start()
    try:
        # Warm-up verwerfen, aber loggen (Prompts-ID ueberschreibbar fuer E3/C3/D5).
        warm_prompt = prompts[test.get("warmup_id", ids[0])]
        warm = chat_stream(make_body(warm_prompt, test, 0), timeout=1800)
        warm_record = {"prompt": warm_prompt["id"], "ttft_s": warm.get("ttft_s"),
                       "wall_s": warm.get("wall_s"), "error": warm.get("error")}
        log(f"Warm-up {test['id']}: {warm_record}")
        # Telemetrie (Pflicht); Timeline-Record nur in separaten Laufen.
        tel = None
        if test.get("telemetry", True):
            tel = TelemetryRecorder(test["id"],
                                    rate_hz=float(test.get("telemetry_rate", 1.0)),
                                    record=bool(test.get("record_timeline", False)))
            tel.start()
        order = [(rep, pid) for rep in range(n) for pid in ids]
        stable = int(hashlib.md5(test["id"].encode("utf-8")).hexdigest()[:8], 16)
        rnd = random.Random(SEED + stable)
        rnd.shuffle(order)
        for rep, pid in order:
            p = prompts[pid]
            result = chat_stream(make_body(p, test, rep), timeout=int(test.get("request_timeout", 1800)))
            t = result.get("timings") or {}
            u = result.get("usage") or {}
            rec = {
                "rep": rep,
                "prompt_id": pid,
                "prompt_sha256": p["sha256"],
                "prompt_target_tokens": p.get("target_tokens"),
                "prompt_tokens": u.get("prompt_tokens") or t.get("prompt_n"),
                "cached_tokens": (u.get("prompt_tokens_details") or {}).get("cached_tokens"),
                "output_tokens": u.get("completion_tokens") or t.get("predicted_n"),
                "decode_tps": round(t["predicted_n"] / (t["predicted_ms"] / 1000), 4)
                if t.get("predicted_n") and t.get("predicted_ms") else None,
                "prefill_tps": round(t["prompt_n"] / (t["prompt_ms"] / 1000), 4)
                if t.get("prompt_n") and t.get("prompt_ms") else None,
                "prompt_ms": t.get("prompt_ms"),
                "decode_ms": t.get("predicted_ms"),
                "ttft_s": result.get("ttft_s"),
                "first_token_kind": result.get("first_token_kind"),
                "wall_s": result.get("wall_s"),
                "draft_n": t.get("draft_n"),
                "draft_accepted": t.get("draft_n_accepted"),
                "acceptance_rate": round(t["draft_n_accepted"] / t["draft_n"], 4)
                if t.get("draft_n") else None,
                "finish": result.get("finish"),
                "error": result.get("error"),
                "content_sha256": hashlib.sha256(result["content"].encode("utf-8")).hexdigest(),
                "content_len": len(result["content"]),
            }
            records.append(rec)
    finally:
        gpu = sampler.stop()
        tel_summary = None
        if tel is not None:
            try:
                tel.capture_heatmap()
                tel_summary = tel.stop()
            except Exception as exc:  # noqa: BLE001
                log(f"Telemetrie-Fehler {test['id']}: {redact(str(exc))}")
                tel_summary = {"error": redact(str(exc))}
    facts1 = collect_engine_facts()
    stop_server(component)
    ok = [r for r in records if not r["error"]]
    summary = {
        "decode_tps": describe([r["decode_tps"] for r in ok]),
        "prefill_tps": describe([r["prefill_tps"] for r in ok]),
        "ttft_s": describe([r["ttft_s"] for r in ok]),
        "wall_s": describe([r["wall_s"] for r in ok]),
        "prompt_tokens": describe([r["prompt_tokens"] for r in ok]),
        "output_tokens": describe([r["output_tokens"] for r in ok]),
        "cached_tokens": describe([r["cached_tokens"] for r in ok]),
        "acceptance_rate": describe([r["acceptance_rate"] for r in ok if r["acceptance_rate"] is not None]),
    }
    disk_delta = None
    if facts0.get("disk_read_mb") is not None and facts1.get("disk_read_mb") is not None:
        disk_delta = round(facts1["disk_read_mb"] - facts0["disk_read_mb"], 2)
    return {
        "status": "complete" if ok else "failed",
        "test_id": test["id"],
        "block": test.get("block"),
        "priority": test.get("priority", 3),
        "label": test.get("label", test["id"]),
        "spec": test.get("spec", {}),
        "config": cfg,
        "health": {k: health.get(k) for k in ("loaded", "model", "max_context")},
        "startup": startup,
        "engine_facts_before": facts0,
        "engine_facts_after": facts1,
        "disk_read_delta_mb": disk_delta,
        "gpu": gpu,
        "telemetry": tel_summary,
        "warmup": warm_record,
        "summary": summary,
        "records": records,
        "errors": [r["error"] for r in records if r["error"]],
        "finished_at": datetime.now().isoformat(timespec="seconds"),
    }


def run_command_test(test: dict, base: dict, component: dict, caps: dict) -> dict:
    """A1 / I1: mitgelieferte Strata-Tools als subprocess ausfuehren."""
    cfg = apply_config(base, test.get("spec", {}))
    write_config(cfg)
    stop_server(component)
    start_server(component, cfg)
    wait_loaded(int(test.get("ready_timeout", 2400)))
    out_path = LOGS / f"{test['id']}.out.txt"
    argv = test["command"]
    started = time.monotonic()
    env = {**os.environ, "TEMP": str(TMP), "TMP": str(TMP), "PYTHONNOUSERSITE": "1"}
    try:
        with out_path.open("w", encoding="utf-8", errors="replace") as fh:
            r = subprocess.run(argv, cwd=test.get("cwd", str(STRATA_DIR)), env=env,
                               stdout=fh, stderr=subprocess.STDOUT,
                               timeout=int(test.get("timeout", 3600)))
        rc, err = r.returncode, None
    except subprocess.TimeoutExpired:
        rc, err = -99, "timeout"
    except Exception as exc:  # noqa: BLE001
        rc, err = -98, redact(str(exc))
    duration = round(time.monotonic() - started, 2)
    stop_server(component)
    return {
        "status": "complete" if rc == 0 else "failed",
        "test_id": test["id"],
        "block": test.get("block"),
        "priority": test.get("priority", 1),
        "label": test.get("label", test["id"]),
        "spec": test.get("spec", {}),
        "config": cfg,
        "command": argv,
        "returncode": rc,
        "error": err,
        "duration_s": duration,
        "output_file": str(out_path),
        "output_tail": out_path.read_text("utf-8", errors="replace")[-4000:] if out_path.exists() else "",
        "finished_at": datetime.now().isoformat(timespec="seconds"),
    }


def run_special_test(test: dict, base: dict, component: dict, caps: dict) -> dict:
    """G3/G4/H2/H4 und aehnliche: Umgebung aendern, HTTP-Test fahren, zurueck."""
    kind = test["kind"]
    spec = test.get("spec", {})
    notes = []
    ok = True
    if kind == "power":
        watts = spec.get("watts")
        ok = set_power_limit(watts)
        notes.append(f"power_limit={watts}W gesetzt={ok}")
        if not ok:
            return {"status": "failed", "test_id": test["id"], "block": test.get("block"),
                    "reason": "Power-Limit nicht aenderbar (keine Admin-Rechte)", "notes": notes,
                    "finished_at": datetime.now().isoformat(timespec="seconds")}
    elif kind == "defender":
        path = spec.get("path", str(STRATA_DIR.parent))
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
                            f"Add-MpPreference -ExclusionPath '{path}'; if($?){{'OK'}}"],
                           capture_output=True, text=True, timeout=120)
        ok = "OK" in r.stdout
        notes.append(f"Defender exclusion set={ok}: {redact((r.stderr or '').strip()[:200])}")
        if not ok:
            return {"status": "failed", "test_id": test["id"], "block": test.get("block"),
                    "reason": "Defender-Ausnahme nicht automatisierbar (keine Admin-Rechte)",
                    "notes": notes, "finished_at": datetime.now().isoformat(timespec="seconds")}
    elif kind == "plan":
        guid = spec.get("guid")
        r = subprocess.run(["powercfg", "/s", guid], capture_output=True, text=True, timeout=60)
        ok = r.returncode == 0
        notes.append(f"Energieplan={guid} gesetzt={ok}")
        if not ok:
            return {"status": "failed", "test_id": test["id"], "block": test.get("block"),
                    "reason": "Energieplan nicht aenderbar (keine Admin-Rechte)", "notes": notes,
                    "finished_at": datetime.now().isoformat(timespec="seconds")}
    try:
        inner = dict(test)
        inner["kind"] = "http"
        res = run_http_test(inner, base, component, caps)
        res["notes"] = notes
        res["special"] = kind
        return res
    finally:
        if kind == "power" and caps.get("power_limit_w_original"):
            set_power_limit(caps["power_limit_w_original"])
        elif kind == "defender":
            subprocess.run(["powershell", "-NoProfile", "-Command",
                            f"Remove-MpPreference -ExclusionPath '{spec.get('path', str(STRATA_DIR.parent))}'"],
                           capture_output=True, text=True, timeout=120)
        elif kind == "plan" and caps.get("power_plan_original"):
            subprocess.run(["powercfg", "/s", caps["power_plan_original"]],
                           capture_output=True, text=True, timeout=60)


def _request_series(test: dict, prompts: dict, reps: int, ids: list[str],
                    warmup_id: str | None = None) -> tuple[list[dict], dict]:
    """Gemeinsame Request-Schleife fuer learning/concurrent/soak/http."""
    records = []
    warm = {"prompt": None, "error": None}
    if warmup_id:
        wp = prompts[warmup_id]
        r = chat_stream(make_body(wp, test, 0), timeout=1800)
        warm = {"prompt": wp["id"], "ttft_s": r.get("ttft_s"), "wall_s": r.get("wall_s"),
                "error": r.get("error")}
    order = [(rep, pid) for rep in range(reps) for pid in ids]
    stable = int(hashlib.md5(test["id"].encode("utf-8")).hexdigest()[:8], 16)
    random.Random(SEED + stable).shuffle(order)
    for rep, pid in order:
        p = prompts[pid]
        r = chat_stream(make_body(p, test, rep), timeout=int(test.get("request_timeout", 1800)))
        t, u = r.get("timings") or {}, r.get("usage") or {}
        records.append({
            "rep": rep, "prompt_id": pid,
            "decode_tps": round(t["predicted_n"] / (t["predicted_ms"] / 1000), 4)
            if t.get("predicted_n") and t.get("predicted_ms") else None,
            "prefill_tps": round(t["prompt_n"] / (t["prompt_ms"] / 1000), 4)
            if t.get("prompt_n") and t.get("prompt_ms") else None,
            "ttft_s": r.get("ttft_s"), "wall_s": r.get("wall_s"),
            "prompt_tokens": u.get("prompt_tokens") or t.get("prompt_n"),
            "output_tokens": u.get("completion_tokens") or t.get("predicted_n"),
            "cached_tokens": (u.get("prompt_tokens_details") or {}).get("cached_tokens"),
            "draft_n": t.get("draft_n"), "draft_accepted": t.get("draft_n_accepted"),
            "error": r.get("error"),
            "content_sha256": hashlib.sha256(r["content"].encode("utf-8")).hexdigest(),
        })
    return records, warm


def run_learning_test(test: dict, base: dict, component: dict, caps: dict) -> dict:
    """E1/E3/E5: mit (optional) geleerten Lerndaten eine Serie fahren und Verlauf speichern."""
    saved = backup_learning()
    if test.get("clear_learning", True):
        clear_learning()
    cfg = apply_config(base, test.get("spec", {}))
    write_config(cfg)
    log_path = CONFIG_PATH.with_suffix(".log")
    offset = log_path.stat().st_size if log_path.exists() else 0
    stop_server(component)
    start_server(component, cfg)
    wait_loaded(int(test.get("ready_timeout", 2400)))
    startup = parse_startup(log_path, offset)
    prompts = load_prompts()
    ids = test.get("prompts") or ["chat_de"]
    sampler = Sampler()
    sampler.start()
    try:
        records, warm = _request_series(test, prompts, int(test.get("n", 100)), ids,
                                        test.get("warmup_id"))
    finally:
        gpu = sampler.stop()
    facts = collect_engine_facts()
    stop_server(component)
    restore_msgs = restore_learning(saved)
    chunks = []
    step = max(1, len(records) // 10)
    for i in range(0, len(records), step):
        part = [r["decode_tps"] for r in records[i:i + step] if r["decode_tps"]]
        chunks.append({"from_request": i, "to_request": min(i + step, len(records)),
                       "decode": describe(part)})
    ok = [r for r in records if not r["error"]]
    return {
        "status": "complete" if ok else "failed", "test_id": test["id"],
        "block": test.get("block"), "priority": test.get("priority", 2),
        "label": test.get("label", test["id"]), "spec": test.get("spec", {}),
        "startup": startup, "engine_facts": facts, "gpu": gpu, "warmup": warm,
        "learning_curve": chunks,
        "summary": {"decode_tps": describe([r["decode_tps"] for r in ok]),
                    "ttft_s": describe([r["ttft_s"] for r in ok])},
        "restore_messages": restore_msgs, "records": records,
        "finished_at": datetime.now().isoformat(timespec="seconds"),
    }


def run_concurrent_test(test: dict, base: dict, component: dict, caps: dict) -> dict:
    """J1: N gleichzeitige Requests, gemessen an der Wandzeit der gesamten Gruppe."""
    cfg = apply_config(base, test.get("spec", {}))
    write_config(cfg)
    stop_server(component)
    start_server(component, cfg)
    wait_loaded(int(test.get("ready_timeout", 2400)))
    prompts = load_prompts()
    p = prompts[test.get("prompts", ["chat_de"])[0]]
    n_parallel = int(test.get("parallel", 2))
    reps = int(test.get("n", 5))
    sampler = Sampler()
    sampler.start()
    results = []
    try:
        for rep in range(reps):
            t0 = time.monotonic()
            with ThreadPoolExecutor(max_workers=n_parallel) as pool:
                rs = list(pool.map(lambda i: chat_stream(make_body(p, test, rep * 10 + i),
                                                        timeout=1800), range(n_parallel)))
            wall = time.monotonic() - t0
            tps = [r["timings"]["predicted_n"] / (r["timings"]["predicted_ms"] / 1000)
                   for r in rs if r.get("timings") and r["timings"].get("predicted_ms")]
            results.append({"rep": rep, "group_wall_s": round(wall, 3),
                            "aggregate_decode_tps": round(sum(tps), 3) if tps else None,
                            "per_request_decode_tps": [round(x, 3) for x in tps],
                            "ttft_s": [r.get("ttft_s") for r in rs],
                            "errors": [r.get("error") for r in rs if r.get("error")]})
    finally:
        gpu = sampler.stop()
    facts = collect_engine_facts()
    stop_server(component)
    return {
        "status": "complete" if any(r["aggregate_decode_tps"] for r in results) else "failed",
        "test_id": test["id"], "block": test.get("block"), "priority": test.get("priority", 4),
        "label": test.get("label", test["id"]), "spec": test.get("spec", {}),
        "parallel": n_parallel, "engine_facts": facts, "gpu": gpu,
        "summary": {"group_wall_s": describe([r["group_wall_s"] for r in results]),
                    "aggregate_decode_tps": describe([r["aggregate_decode_tps"] for r in results])},
        "records": results, "finished_at": datetime.now().isoformat(timespec="seconds"),
    }


def run_soak_test(test: dict, base: dict, component: dict, caps: dict) -> dict:
    """J2: 1-2 h gemischter Workload, Speed-Verlauf und Leaks."""
    cfg = apply_config(base, test.get("spec", {}))
    write_config(cfg)
    stop_server(component)
    start_server(component, cfg)
    wait_loaded(int(test.get("ready_timeout", 2400)))
    prompts = load_prompts()
    ids = test.get("prompts") or ["chat_de", "chat_en", "coding", "math_reasoning", "long_4k"]
    duration = int(test.get("duration_s", 5400))
    deadline = time.monotonic() + duration
    sampler = Sampler()
    sampler.start()
    records = []
    try:
        i = 0
        while time.monotonic() < deadline and not _state["stop"]:
            p = prompts[ids[i % len(ids)]]
            r = chat_stream(make_body(p, test, i), timeout=1800)
            t, u = r.get("timings") or {}, r.get("usage") or {}
            records.append({"i": i, "at_s": round(time.monotonic() - (deadline - duration), 1),
                            "prompt_id": p["id"],
                            "decode_tps": round(t["predicted_n"] / (t["predicted_ms"] / 1000), 3)
                            if t.get("predicted_n") and t.get("predicted_ms") else None,
                            "error": r.get("error")})
            if i % 25 == 0:
                log(f"  soak {i}: decode={records[-1]['decode_tps']} "
                    f"ram={psutil.virtual_memory().percent}%")
            i += 1
    finally:
        gpu = sampler.stop()
    facts = collect_engine_facts()
    stop_server(component)
    chunks = []
    step = max(1, len(records) // 10)
    for j in range(0, len(records), step):
        part = [r["decode_tps"] for r in records[j:j + step] if r["decode_tps"]]
        chunks.append({"request_range": [j, min(j + step, len(records))], "decode": describe(part),
                       "errors": sum(1 for r in records[j:j + step] if r["error"])})
    return {
        "status": "complete" if records else "failed", "test_id": test["id"],
        "block": test.get("block"), "priority": test.get("priority", 4),
        "label": test.get("label", test["id"]), "spec": test.get("spec", {}),
        "duration_s": duration, "engine_facts": facts, "gpu": gpu,
        "phases": chunks, "summary": {"decode_tps": describe([r["decode_tps"] for r in records if r["decode_tps"]])},
        "record_count": len(records), "finished_at": datetime.now().isoformat(timespec="seconds"),
    }


def run_error_test(test: dict, base: dict, component: dict, caps: dict) -> dict:
    """J3: Abbruch mitten im Prefill und zu grosser Prompt."""
    cfg = apply_config(base, test.get("spec", {}))
    write_config(cfg)
    stop_server(component)
    start_server(component, cfg)
    wait_loaded(int(test.get("ready_timeout", 2400)))
    prompts = load_prompts()
    mode = test.get("mode", "oversized")
    observations = []
    try:
        if mode == "oversized":
            p = prompts.get("long_200k") or prompts["long_128k"]
            r = chat_stream(make_body(p, test, 0), timeout=900)
            observations.append({"case": "oversized_prompt", "error": r.get("error"),
                                 "wall_s": r.get("wall_s"), "finish": r.get("finish")})
        else:
            import requests as _rq
            p = prompts["long_128k"]
            body = make_body(p, test, 0)
            try:
                with _rq.post(BASE_URL + "/v1/chat/completions", json=body, stream=True,
                              timeout=(30, 900), headers={"Origin": BASE_URL}) as resp:
                    for i, _ in enumerate(resp.iter_lines()):
                        if i >= 5:
                            break
                observations.append({"case": "abort_mid_prefill", "result": "client disconnected"})
            except Exception as exc:  # noqa: BLE001
                observations.append({"case": "abort_mid_prefill", "error": redact(str(exc))})
            time.sleep(20)
            h = http_json(BASE_URL + "/health", timeout=10)
            observations.append({"case": "health_after_abort", "loaded": h.get("loaded"),
                                 "status": h.get("status")})
    finally:
        stop_server(component)
    return {"status": "complete", "test_id": test["id"], "block": test.get("block"),
            "priority": test.get("priority", 4), "label": test.get("label", test["id"]),
            "mode": mode, "observations": observations,
            "finished_at": datetime.now().isoformat(timespec="seconds")}


def run_test(test: dict, base: dict, component: dict, caps: dict) -> dict:
    kind = test.get("kind", "http")
    if kind == "http":
        return run_http_test(test, base, component, caps)
    if kind == "command":
        return run_command_test(test, base, component, caps)
    if kind in ("power", "defender", "plan"):
        return run_special_test(test, base, component, caps)
    if kind == "learning":
        return run_learning_test(test, base, component, caps)
    if kind == "concurrent":
        return run_concurrent_test(test, base, component, caps)
    if kind == "soak":
        return run_soak_test(test, base, component, caps)
    if kind == "error":
        return run_error_test(test, base, component, caps)
    return {"status": "failed", "test_id": test["id"], "reason": f"unbekannter kind={kind}"}


# ---------------------------------------------------------------- learning data

def backup_learning() -> dict:
    dest = CONFIGS / "learning-backup"
    dest.mkdir(parents=True, exist_ok=True)
    saved = {}
    for p in LEARN_FILES:
        if p.exists():
            target = dest / p.name
            shutil.copy2(p, target)
            saved[str(p)] = sha256_file(target)
    return saved


def clear_learning() -> None:
    for p in LEARN_FILES:
        if p.exists():
            p.rename(p.with_name(p.name + ".bench-off"))


def restore_learning(saved: dict) -> list[str]:
    msgs = []
    for p in LEARN_FILES:
        off = p.with_name(p.name + ".bench-off")
        if off.exists():
            if p.exists():
                p.unlink()
            off.rename(p)
            msgs.append(f"{p.name}: wiederhergestellt")
    for p in LEARN_FILES:
        expected = saved.get(str(p))
        if p.exists() and expected and sha256_file(p) == expected:
            msgs.append(f"{p.name}: Hash verifiziert")
        elif p.exists():
            msgs.append(f"{p.name}: Hash ABWEICHEND")
    return msgs


# ---------------------------------------------------------------- main

def final_restore(base_cfg: dict, component: dict, caps: dict, saved_learning: dict) -> dict:
    report = {"at": datetime.now().isoformat(timespec="seconds"), "actions": []}
    # Lerndaten zuerst, damit ein neu gestarteter Engine sie sieht.
    for msg in restore_learning(saved_learning):
        report["actions"].append(msg)
    write_config(base_cfg)
    actual = sha256_file(CONFIG_PATH)
    expected = sha256_file(ORIGINAL_CONFIG)
    report["config_hash"] = actual
    report["config_matches_original"] = actual == expected
    report["actions"].append(f"Config wiederhergestellt: {actual == expected}")
    if caps.get("power_limit_w_original"):
        ok = set_power_limit(caps["power_limit_w_original"])
        report["power_limit_restored"] = ok
        report["actions"].append(f"Power-Limit {caps['power_limit_w_original']} W: {ok}")
    if caps.get("power_plan_original"):
        r = subprocess.run(["powercfg", "/s", caps["power_plan_original"]],
                           capture_output=True, text=True, timeout=60)
        report["power_plan_restored"] = r.returncode == 0
        report["actions"].append(f"Energieplan: {r.returncode == 0}")
    # Keine Defender-Ausnahme darf uebrig bleiben.
    r = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "Remove-MpPreference -ExclusionPath 'C:\\Users\\[USER]\\Desktop\\python.toolz\\apps' 2>$null; 'done'"],
                       capture_output=True, text=True, timeout=120)
    report["actions"].append("Defender-Ausnahme-Entfernung versucht")
    try:
        stop_server(component)
        start_server(component, base_cfg)
        h = wait_loaded(2400)
        report["engine_restarted_loaded"] = bool(h.get("loaded"))
        report["actions"].append(f"Engine neu gestartet: {h.get('loaded')}")
        nf = collect_engine_facts()
        report["final_engine_facts"] = nf
    except Exception as exc:  # noqa: BLE001
        report["engine_restarted_loaded"] = False
        report["actions"].append("Engine-Neustart FEHLGESCHLAGEN: " + redact(str(exc)))
    jdump(report, ROOT / "RESTORE_REPORT.json")
    lines = ["# RESTORE_REPORT", ""]
    for k, v in report.items():
        lines.append(f"- **{k}:** {json.dumps(v, ensure_ascii=False)}")
    (ROOT / "RESTORE_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    log("Wiederherstellung abgeschlossen: " + json.dumps(report, ensure_ascii=False)[:600])
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=ROOT / "runner" / "matrix.yaml")
    parser.add_argument("--only", default=None, help="Komma-getrennte Block-IDs, z.B. P1 oder A1,B1")
    parser.add_argument("--skip", default=None, help="Komma-getrennte Test-IDs")
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--no-restore", action="store_true")
    parser.add_argument("--clear-learning", action="store_true", help="Lerndaten vor dem Lauf leeren (E1)")
    opts = parser.parse_args(argv)

    for d in (RESULTS, LOGS, TMP, CONFIGS):
        d.mkdir(parents=True, exist_ok=True)
    os.environ["TEMP"] = str(TMP)
    os.environ["TMP"] = str(TMP)
    tempfile.tempdir = str(TMP)
    log("=== Runner gestartet ===")

    matrix = yaml.safe_load(opts.matrix.read_text("utf-8"))
    defaults = matrix.get("defaults", {})
    tests = []
    for t in matrix["tests"]:
        merged = dict(defaults)
        merged.update(t)
        # spec tief zusammenfuehren: der globale Default (Reserve 512) darf nicht
        # durch einen Test-Spec mit eigenen args/env verloren gehen.
        dspec = dict(defaults.get("spec") or {})
        tspec = dict(t.get("spec") or {})
        spec = {**dspec, **tspec}
        for key in ("args", "env", "config_keys"):
            sub = {**(dspec.get(key) or {}), **(tspec.get(key) or {})}
            if sub:
                spec[key] = sub
        merged["spec"] = spec
        tests.append(merged)

    only = set(opts.only.split(",")) if opts.only else None
    skip = set(opts.skip.split(",")) if opts.skip else set()
    if only:
        tests = [t for t in tests if t.get("block") in only or t["id"] in only]
    tests = [t for t in tests if t["id"] not in skip]

    base_cfg = jload(ORIGINAL_CONFIG)
    component = tracker_component()
    caps = probe_capabilities()

    saved_learning = {}
    if opts.clear_learning:
        saved_learning = backup_learning()
        clear_learning()
        log("Lerndaten geleert (Backup in configs/learning-backup)")

    # Prioritaet zuerst, innerhalb des Blocks randomisiert (gegen Drift).
    tests.sort(key=lambda t: (int(t.get("priority", 3)), str(t.get("block", ""))))
    grouped: dict[tuple, list] = {}
    for t in tests:
        grouped.setdefault((int(t.get("priority", 3)), str(t.get("block", ""))), []).append(t)
    ordered = []
    for key in sorted(grouped):
        block = grouped[key]
        rnd = random.Random(SEED + sum(ord(c) for c in key[1]))
        rnd.shuffle(block)
        ordered.extend(block)

    state = jload(ROOT / "STATE.md.json") if (ROOT / "STATE.md.json").exists() else {}
    state.update({"phase": 3, "total": len(ordered), "done": 0,
                  "started_at": datetime.now().isoformat(timespec="seconds")})
    jdump(state, ROOT / "STATE.md.json")

    exit_code = 0
    try:
        for i, test in enumerate(ordered, 1):
            tid = test["id"]
            out = RESULTS / f"{tid}.json"
            if out.exists():
                try:
                    old = jload(out)
                    if old.get("status") == "complete":
                        log(f"[{i}/{len(ordered)}] SKIP {tid} (bereits complete)")
                        state["done"] += 1
                        jdump(state, ROOT / "STATE.md.json")
                        continue
                except ValueError:
                    pass
            log(f"[{i}/{len(ordered)}] START {tid} P{test.get('priority')} {test.get('label','')}")
            result = None
            for attempt in range(opts.retries + 1):
                try:
                    result = run_test(test, base_cfg, component, caps)
                    if result.get("status") == "complete":
                        break
                    log(f"  Versuch {attempt + 1} nicht erfolgreich: {result.get('reason') or result.get('errors')}")
                except Exception as exc:  # noqa: BLE001
                    result = {"status": "failed", "test_id": tid, "error": redact(str(exc)),
                              "traceback": redact(traceback.format_exc()[-2000:])}
                    log(f"  Exception Versuch {attempt + 1}: {result['error'][:300]}")
                if attempt < opts.retries:
                    log("  Retry nach Engine-Neustart ...")
                    try:
                        stop_server(component)
                        write_config(base_cfg)
                        start_server(component, base_cfg)
                        wait_loaded(2400)
                    except Exception as exc:  # noqa: BLE001
                        log("  Retry-Vorbereitung fehlgeschlagen: " + redact(str(exc)))
            result = result or {"status": "failed", "test_id": tid, "reason": "kein Ergebnis"}
            result["attempts"] = opts.retries + 1
            jdump(result, out)
            state["done"] += 1
            state["last"] = tid
            jdump(state, ROOT / "STATE.md.json")
            log(f"  -> {result.get('status')} {out.name}")
    except KeyboardInterrupt:
        log("Unterbrochen → Wiederherstellung")
        exit_code = 130
    finally:
        if not opts.no_restore:
            try:
                final_restore(jload(ORIGINAL_CONFIG), component, caps, saved_learning)
            except Exception as exc:  # noqa: BLE001
                log("Wiederherstellung FEHLGESCHLAGEN: " + redact(str(exc)))
                exit_code = 2
        state["phase"] = 4
        state["finished_at"] = datetime.now().isoformat(timespec="seconds")
        jdump(state, ROOT / "STATE.md.json")
    log(f"=== Runner Ende, code={exit_code} ===")
    return exit_code


if __name__ == "__main__":
    import tempfile
    raise SystemExit(main())
