"""Live-Telemetrie-Recorder für den Strata-HotRod-Monitor.

Datenquelle: GET /metrics (1 Hz, native Rate des Monitor-Frontends) und
POST /v1/monitor/timeline {"on": bool} fuer den Record-Schalter.
Kein Screenshot/OCR. Alle Daten mit Zeitstempel + Run-ID als JSONL.
"""
from __future__ import annotations

import json
import os
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
TELEMETRY = ROOT / "telemetry"
BASE_URL = "http://127.0.0.1:8080"


def http_json(url: str, body=None, timeout: int = 15, origin: str = BASE_URL):
    headers = {"Content-Type": "application/json", "Origin": origin}
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8") if body is not None else None,
        headers=headers,
        method="POST" if body is not None else "GET",
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(req, timeout=timeout) as resp:
        return json.load(resp)


def set_record(on: bool) -> dict:
    """Record-Schalter des Monitors (front-end: POST v1/monitor/timeline)."""
    r = http_json(BASE_URL + "/v1/monitor/timeline", {"on": bool(on)})
    return r


def record_status() -> bool:
    try:
        m = http_json(BASE_URL + "/metrics")
        return bool((m.get("timeline") or {}).get("on"))
    except Exception:  # noqa: BLE001
        return False


class TelemetryRecorder:
    def __init__(self, run_id: str, rate_hz: float = 1.0, record: bool = False):
        self.run_id = run_id
        self.rate = float(rate_hz)
        self.record = bool(record)
        self.lines: list[dict] = []
        self.timeline_rows: list[list] = []
        self.reads: list[list] = []
        self.gaps: list[list] = []
        self.error: str | None = None
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._after = None
        self._base = None
        self.record_actually_on = False
        TELEMETRY.mkdir(parents=True, exist_ok=True)
        self.jsonl = TELEMETRY / f"{run_id}.jsonl"
        self.summary = TELEMETRY / f"{run_id}-summary.json"

    def start(self) -> None:
        if self.record:
            try:
                set_record(True)
                self.record_actually_on = record_status()
            except Exception as exc:  # noqa: BLE001
                self.error = f"record start: {exc}"
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                q = ""
                if self._after is not None and self._base is not None:
                    q = f"?tl_after={self._after}&tl_base={self._base}"
                m = http_json(BASE_URL + "/metrics" + q, timeout=20)
                live = m.get("live") or {}
                hw = m.get("hardware") or {}
                eng = m.get("engine") or {}
                res = m.get("residency") or {}
                conv = m.get("conversation_cache") or {}
                tl = m.get("timeline") or {}
                data = tl.get("data") or {}
                if data.get("reset"):
                    self.timeline_rows.clear()
                    self.reads.clear()
                    self.gaps.clear()
                if data.get("layers"):
                    self.timeline_rows.extend(data["layers"])
                if data.get("reads"):
                    self.reads.extend(data["reads"])
                if data.get("gaps"):
                    self.gaps.extend(data["gaps"])
                self._after = data.get("last", self._after)
                self._base = data.get("base_ns", self._base)
                self.lines.append({
                    "ts": time.time(),
                    "run_id": self.run_id,
                    "state": live.get("state"),
                    "decode_tok_s": live.get("tok_s"),
                    "decode_tok_s_mean": live.get("tok_s_mean"),
                    "prefill_tok_s_mean": live.get("prefill_tok_s_mean"),
                    "prompt_read": live.get("prompt_read"),
                    "prompt_total": live.get("prompt_total"),
                    "generated": live.get("generated"),
                    "queued": live.get("queued"),
                    "gpu_util": hw.get("gpu_util"),
                    "vram_used": hw.get("gpu_mem_used"),
                    "vram_total": hw.get("gpu_mem_total"),
                    "gpu_temp": hw.get("gpu_temp"),
                    "gpu_power_w": hw.get("gpu_power"),
                    "gpu_power_limit_w": hw.get("gpu_power_limit"),
                    "pcie_gen": hw.get("gpu_pcie_gen"),
                    "pcie_width": hw.get("gpu_pcie_width"),
                    "pcie_rx_mb": hw.get("gpu_pcie_rx_mb"),
                    "pcie_tx_mb": hw.get("gpu_pcie_tx_mb"),
                    "cpu_pct": hw.get("cpu"),
                    "ram_used": hw.get("ram_used"),
                    "ram_total": hw.get("ram_total"),
                    "disk_read_mb": hw.get("disk_read_mb"),
                    "disk_write_mb": hw.get("disk_write_mb"),
                    "expert_slots": eng.get("expert_slots"),
                    "vram_free_mib": eng.get("vram_free_mib"),
                    "resident_experts": res.get("resident"),
                    "experts_total": (res.get("layers") or 0) * (res.get("experts") or 0) or None,
                    "swaps": res.get("swaps"),
                    "rounds": res.get("round"),
                    "quality_swaps": res.get("quality_swaps"),
                    "conv_requests": conv.get("requests"),
                    "conv_reused_tokens": conv.get("reused_tokens"),
                    "timeline_on": tl.get("on"),
                    "timeline_rows": len(self.timeline_rows),
                    "timeline_gaps": len(self.gaps),
                })
            except Exception as exc:  # noqa: BLE001
                self.error = f"poll: {exc}"
            self._stop.wait(1.0 / max(0.1, self.rate))

    def stop(self) -> dict:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)
        if self.record:
            try:
                set_record(False)
            except Exception as exc:  # noqa: BLE001
                self.error = (self.error or "") + f" record stop: {exc}"
        # JSONL schreiben (ohne interne Liste zu implizieren)
        with self.jsonl.open("w", encoding="utf-8") as fh:
            for line in self.lines:
                fh.write(json.dumps(line, ensure_ascii=False) + "\n")
        result = self._summarize()
        self.summary.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                                encoding="utf-8")
        (TELEMETRY / f"{self.run_id}-timeline.json").write_text(
            json.dumps({"run_id": self.run_id, "layers": self.timeline_rows,
                        "reads": self.reads, "gaps": self.gaps}, ensure_ascii=False) + "\n",
            encoding="utf-8")
        return result

    def _series(self, key):
        return [float(x[key]) for x in self.lines if isinstance(x.get(key), (int, float))]

    def _stats(self, key):
        v = self._series(key)
        return {"n": len(v), "mean": round(float(np.mean(v)), 3) if v else None,
                "median": round(float(np.median(v)), 3) if v else None,
                "max": round(float(np.max(v)), 3) if v else None,
                "min": round(float(np.min(v)), 3) if v else None}

    def _summarize(self) -> dict:
        first = self.lines[0] if self.lines else {}
        last = self.lines[-1] if self.lines else {}
        res = {
            "run_id": self.run_id,
            "samples": len(self.lines),
            "duration_s": round(last.get("ts", 0) - first.get("ts", 0), 2) if self.lines else 0,
            "error": self.error,
            "record_requested": self.record,
            "record_actually_on": self.record_actually_on,
            "series": {k: self._stats(k) for k in (
                "decode_tok_s", "gpu_util", "vram_used", "gpu_temp", "gpu_power_w",
                "pcie_rx_mb", "pcie_tx_mb", "cpu_pct", "disk_read_mb", "disk_write_mb",
                "resident_experts", "swaps", "rounds")},
            "experts": {
                "resident_start": first.get("resident_experts"),
                "resident_end": last.get("resident_experts"),
                "total": last.get("experts_total"),
                "swaps_start": first.get("swaps"),
                "swaps_end": last.get("swaps"),
                "rounds_start": first.get("rounds"),
                "rounds_end": last.get("rounds"),
                "quality_swaps": last.get("quality_swaps"),
            },
            "conversation_cache": {
                "requests": last.get("conv_requests"),
                "reused_tokens": last.get("conv_reused_tokens"),
            },
            "timeline": {
                "on": last.get("timeline_on"),
                "windows": len({r[0] for r in self.timeline_rows if len(r) > 0}),
                "rows": len(self.timeline_rows),
                "reads": len(self.reads),
                "gaps": len(self.gaps),
                "gap_windows_lost": sum(int(g[1]) for g in self.gaps if len(g) > 1 and isinstance(g[1], (int, float))),
            },
            "jsonl": str(self.jsonl),
        }
        # Swaps pro Runde / pro Token
        ds, de = res["experts"]["swaps_start"], res["experts"]["swaps_end"]
        rs, re_ = res["experts"]["rounds_start"], res["experts"]["rounds_end"]
        if ds is not None and de is not None and rs is not None and re_ is not None and re_ > rs:
            res["experts"]["swaps_per_round"] = round((de - ds) / (re_ - rs), 3)
        # Heatmap-Snapshot (Rohdaten pro Layer/Experte) wird am Ende separat geholt.
        res["heatmap"] = self._heatmap
        return res

    # Heatmap wird beim letzten Poll separat geholt (gross, nicht in jeder JSONL-Zeile).
    _heatmap = None

    def capture_heatmap(self) -> None:
        try:
            m = http_json(BASE_URL + "/metrics", timeout=20)
            r = m.get("residency") or {}
            self._heatmap = {"layers": r.get("layers"), "experts": r.get("experts"),
                             "rows": r.get("rows"), "resident": r.get("resident"),
                             "swaps": r.get("swaps"), "round": r.get("round"),
                             "quality_swaps": r.get("quality_swaps")}
            out = TELEMETRY / f"{self.run_id}-heatmap.json"
            out.write_text(json.dumps(self._heatmap, ensure_ascii=False) + "\n", encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            self.error = (self.error or "") + f" heatmap: {exc}"
