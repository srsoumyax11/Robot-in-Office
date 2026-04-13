# Work Activity Automator

🚀 A lightweight Python terminal tool that helps keep a desktop session active by simulating small keyboard, tab, and mouse actions.

> Designed for personal productivity workflows where you want gentle, configurable activity while you step away or switch context.

## ✨ Features

- 🟢 **Just keep active mode**: sends simple `DOWN` and `UP` key presses every minute.
- 🌐 **Browser automation**: scrolls through browser tabs with low or high intensity presets.
- 💻 **IDE automation**: moves through IDE tabs and simulates activity using configurable timings.
- 🖱️ **Mouse automation**: adds optional random scroll movement in the background.
- ⚙️ **Editable configuration**: tune durations, wait times, tab ranges, key press counts, and mouse behavior in `configuration.py`.
- 🧭 **Keyboard-driven menu**: use arrow keys and `Enter` to choose options.

## 📁 Project Structure

```text
Robot-in-Office/
├── main.py              # Main terminal application
├── configuration.py     # Runtime settings and automation presets
├── requirement.txt      # Python dependency list
└── README.md            # Project documentation
```

## ✅ Requirements

- Python 3.8+
- `pynput`
- A desktop session that allows keyboard and mouse automation

### Linux Note

`pynput` has limited support on Wayland. If you see a Wayland warning, log out and choose an Xorg session such as **Ubuntu on Xorg** or **GNOME on Xorg** from the login screen.

## 🛠️ Installation

Clone or open this project, then install the dependency:

```bash
pip install -r requirement.txt
```

On some Linux systems, you may need the system package instead:

```bash
sudo apt install python3-pynput
```

## ▶️ Run

Start the app from the project directory:

```bash
python main.py
```

If your system uses `python3`:

```bash
python3 main.py
```

## 🎮 How To Use

1. Run the app.
2. Use `Up` / `Down` arrows to select menu options.
3. Press `Enter` to confirm.
4. Choose one of the workflows:
   - **Just keep active** for simple periodic activity.
   - **Browser automation** for tab and page activity.
   - **IDE automation** for editor tab and page activity.
   - **Mouse automation** for random scroll movement.
5. Press `Ctrl+C` anytime to stop.

## ⚙️ Configuration

Edit `configuration.py` to tune automation behavior:

```python
INITIAL_DELAY = 5
KEY_PRESS_INTERVAL = 0.3
TAB_SWITCH_DELAY = 2
```

Preset activity settings live inside `WORK_SETTINGS`:

```python
WORK_SETTINGS = {
    "IDE": {
        "low": {
            "session_duration": 300,
            "tab_range": (1, 2),
            "press_range": (2, 4),
            "wait_range": (10, 20),
        }
    }
}
```

Mouse scrolling is controlled by `MOUSE_CONFIG`:

```python
MOUSE_CONFIG = {
    "scroll_range": (-3, 3),
    "sleep_range": (5, 10)
}
```

## 🧪 Example Session

```bash
python main.py
```

Then choose:

```text
Just keep active? -> No
Want browser automation? -> Yes
Browser Intensity? -> low
Want IDE automation? -> Yes
IDE Intensity? -> high
Want mouse automation? -> Yes
```

The app will show a summary, wait for the configured initial delay, and begin the selected automation loop.

## 🛑 Stop The App

Use:

```bash
Ctrl+C
```

The program catches the interrupt and exits cleanly.

## ⚠️ Responsible Use

This tool controls your keyboard and mouse. Before running it, make sure the active windows are safe for simulated input, and avoid using it in contexts where automation is restricted by policy.

