# Blade Runner Photo ("ENHANCE")

## Project Overview

This project is a prototype for a "Blade Runner" style photo viewer ("ENHANCE") that supports smooth zooming and panning animations controlled via a local TCP socket. It is designed to be controlled programmatically, enabling integration with LLMs or other external tools to simulate voice or text-based image manipulation commands.

## ⚠️ Critical Operational Rules (Calibrated)

These rules are established based on user testing. **Always** follow these direction mappings when controlling the viewer.

### 1. Coordinate System
The viewer uses standard screen coordinates (Top-Left is 0,0).
*   **Left**: Negative X (`dx = -200`)
*   **Right**: Positive X (`dx = +200`)
*   **Up**: Negative Y (`dy = -200`)
*   **Down**: Positive Y (`dy = +200`)

### 2. Launch Environment
**DO NOT** use the default system Python or Anaconda. You **MUST** use the clean `uv` virtual environment located in `.venv`.

*   **Python Executable:** `.venv\Scripts\python.exe`

## Components

1.  **Viewer (`enhance_viewer.py`):**
    *   The GUI Application.
    *   Must be launched first.
    *   Listens on `127.0.0.1:8765`.

2.  **Controller (`photoctl.py`):**
    *   CLI tool to send commands to the Viewer.

3.  **Voice Emulator (`voice_cmd.py`):**
    *   Interactive CLI for natural language commands (Russian supported).

## Usage Instructions

### 1. Start the Viewer
Open a terminal and run the viewer using the isolated environment:
```powershell
.venv\Scripts\python enhance_viewer.py sample.png
```
*The "ENHANCE" window will appear.*

### 2. Control the Viewer
Open a **second** terminal and send commands using the same environment.

#### Zoom
```powershell
# Zoom In (Closer)
.venv\Scripts\python photoctl.py zoom 2.0 500

# Zoom Out (Further)
.venv\Scripts\python photoctl.py zoom 0.5 500
```

#### Pan (Move)
```powershell
# Move Left
.venv\Scripts\python photoctl.py pan -200 0 300

# Move Right
.venv\Scripts\python photoctl.py pan 200 0 300

# Move Up
.venv\Scripts\python photoctl.py pan 0 -200 300

# Move Down
.venv\Scripts\python photoctl.py pan 0 200 300
```

#### Enhance / Reset
```powershell
# Enhance (Sharpen)
.venv\Scripts\python photoctl.py sharpen 1.5

# Reset to Original
.venv\Scripts\python photoctl.py reset_image
```

## Protocol (TCP JSON)

The viewer listens for newline-delimited JSON objects on `127.0.0.1:8765`.

**Example Payload:**
```json
{"cmd": "zoom", "factor": 1.5, "ms": 500}
```
