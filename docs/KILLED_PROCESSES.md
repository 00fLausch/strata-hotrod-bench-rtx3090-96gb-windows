# Stopped background processes

Goal: clean measurement conditions. This list is included in the report and
the final summary. OpenCode itself, the Python Tracker/watcher, MCP helpers and
ChatGPT were **not** stopped.

| Process | PID (at start) | Reason | Restart manually? |
|---|---|---|---|
| Opera GX (browser) | 76340, 73432, plus children | Browser creates GPU/CPU load (explicitly allowed) | Yes |
| ComfyUI (python_embeded) | 30756 | GPU-heavy background service (explicitly listed) | Yes |
| UnrealEditor | 65704 | Significant GPU/CPU load ("etc."); **unsaved changes may have been lost** | Yes, with LiveCoding |
| LiveCodingConsole | 67844 | Belongs to UnrealEditor | Yes, with Unreal |
| Sunshine / sunshinesvc | 8400, 5060 | Attempted; access denied (service), still running | Still running - no action needed |

Time: 2026-11-23, phase 2 and after reboot. All PIDs were verified before the
stop. After the reboot, Opera, ComfyUI and Unreal returned via autostart and
were stopped again; Sunshine could not be stopped.
