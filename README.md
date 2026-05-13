# Jarvis — App & Browser Control Engine

## Architecture

```
Voice/Text Input
     │
     ▼
 NLP / Parser  ──► intent dict  {"intent": "open_app", "app": "chrome"}
     │
     ▼
 action_engine.execute(intent)
     │
     ├── _open_app()   → subprocess.Popen([exe_path])
     ├── _close_app()  → taskkill / osascript / pkill
     ├── _open_url()   → Chrome exe / os.startfile / xdg-open
     └── _run()        → generic platform cmd map
     │
     ▼
  speak()  →  TTS feedback
```

## Intent Reference

| Intent          | Required keys        | Example                                              |
|-----------------|----------------------|------------------------------------------------------|
| `open_app`      | `app`                | `{"intent":"open_app","app":"chrome"}`               |
| `close_app`     | `app`                | `{"intent":"close_app","app":"vlc"}`                 |
| `open_url`      | `url`                | `{"intent":"open_url","url":"youtube.com"}`          |
| `open_browser`  | *(optional)* `app`   | `{"intent":"open_browser"}`                          |
| `screenshot`    | —                    | `{"intent":"screenshot"}`                            |
| `mute`          | —                    | `{"intent":"mute"}`                                  |
| `unmute`        | —                    | `{"intent":"unmute"}`                                |
| `volume_up`     | —                    | `{"intent":"volume_up"}`                             |
| `volume_down`   | —                    | `{"intent":"volume_down"}`                           |
| `brightness_up` | —                    | `{"intent":"brightness_up"}`                         |
| `brightness_down`| —                   | `{"intent":"brightness_down"}`                       |
| `lock`          | —                    | `{"intent":"lock"}`                                  |
| `sleep`         | —                    | `{"intent":"sleep"}`                                 |
| `shutdown`      | —                    | `{"intent":"shutdown"}`                              |
| `restart`       | —                    | `{"intent":"restart"}`                               |
| `wifi_on`       | —                    | `{"intent":"wifi_on"}`                               |
| `wifi_off`      | —                    | `{"intent":"wifi_off"}`                              |
| `empty_trash`   | —                    | `{"intent":"empty_trash"}`                           |
| `query_time`    | —                    | `{"intent":"query_time"}`                            |
| `query_date`    | —                    | `{"intent":"query_date"}`                            |
| `query_battery` | —                    | `{"intent":"query_battery"}`                         |
| `query_ram`     | —                    | `{"intent":"query_ram"}`                             |
| `memory_save`   | `key`, `value`       | `{"intent":"memory_save","key":"name","value":"Ali"}`|
| `memory_recall` | `key`                | `{"intent":"memory_recall","key":"name"}`            |
| `memory_forget` | `key`                | `{"intent":"memory_forget","key":"name"}`            |
| `ask_claude`    | `text`               | `{"intent":"ask_claude","text":"What is RAM?"}`      |
| `repeat`        | —                    | `{"intent":"repeat"}`                                |
| `exit`          | —                    | `{"intent":"exit"}`                                  |

## Supported Apps (Windows — pre-mapped to exe paths)

`chrome`, `edge`, `vlc`, `winrar`, `bluestacks`, `notepad`, `explorer`,
`calc`, `cmd`, `taskmgr`, `control`, `mspaint`, `wordpad`, `excel`,
`word`, `powerpoint`, `outlook`, `itunes`, `virtualdj`, `coreldraw`,
`git`, `node`, `smadav`

## Adding a New App

In `action_engine.py`, add to `WIN_EXE_PATHS`:
```python
"myapp": r"C:\Program Files\MyApp\myapp.exe",
```
And to `WIN_PROC_NAMES`:
```python
"myapp": "myapp.exe",
```

## Quick Test

```python
from action_engine import execute

execute({"intent": "open_app",  "app": "chrome"})
execute({"intent": "open_url",  "url": "youtube.com"})
execute({"intent": "query_time"})
execute({"intent": "screenshot"})
execute({"intent": "close_app", "app": "chrome"})
```

## Dependencies

```
pip install psutil anthropic
```
`psutil` → battery + RAM queries  
`anthropic` → AI fallback via `ask_claude`