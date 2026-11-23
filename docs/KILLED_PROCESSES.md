# Beendete Hintergrundprozesse

Ziel: saubere Messbedingungen. Diese Liste wird im Bericht und in der Abschlussmeldung wiederholt.
OpenCode selbst, der Python-Tracker/Watcher, MCP-Helfer und ChatGPT wurden **nicht** beendet.

| Prozess | PID (bei Start) | Grund | Wieder starten? |
|---|---|---|---|
| Opera GX (Browser) | 76340, 73432 | Browser erzeugt GPU-/CPU-Last (explizit erlaubt) | Ja, manuell |
| ComfyUI (python_embeded) | 30756 | GPU-lastender Hintergrunddienst (explizit genannt) | Ja, manuell |
| UnrealEditor | 65704 | erhebliche GPU-/CPU-Last ("störend … usw."); **ungerettete Änderungen können verloren sein** | Ja, manuell |
| LiveCodingConsole | 67844 | zu UnrealEditor gehörig | Ja, mit Unreal |

Zeitpunkt: 2026-11-23, Phase 2. AllePIDs wurden vor dem Beenden verifiziert.
