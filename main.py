import os
import sys
import time
import random
import threading
import importlib.util
from pathlib import Path

# --- Environment & OS Compatibility Check ---
if sys.platform.startswith("linux"):
    if os.environ.get("WAYLAND_DISPLAY"):
        print("\033[91mError: Wayland Display Manager is currently active.\033[0m")
        print("\033[93mThe 'pynput' library native features are severely restricted on Wayland.\033[0m")
        print("Please log out and change your session:")
        print("1. Click your username on the login screen")
        print("2. Click the gear/cog wheel icon in the bottom right corner")
        print("3. Select \033[96m'Ubuntu on Xorg'\033[0m or \033[96m'GNOME on Xorg'\033[0m")
        print("4. Log back in and run this application again.\n")
        sys.exit(1)

try:
    from pynput.keyboard import Controller as KeyboardController, Key
    from pynput.mouse import Controller as MouseController
except ImportError:
    print("\033[91mError: Required library 'pynput' is not installed.\033[0m")
    if sys.platform.startswith("linux"):
        print("Please install it globally by running:")
        print("\033[93msudo apt install python3-pynput\033[0m")
    else:
        print("Please install it using pip:")
        print("\033[93mpip install pynput\033[0m")
    sys.exit(1)

# Platform specific UI helpers
if sys.platform.startswith("win"):
    import msvcrt
    def clear_screen():
        os.system("cls")
    
    def read_key():
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key in (b'\x00', b'\xe0'):
                    arrow = msvcrt.getch()
                    if arrow == b'H': return "up"
                    if arrow == b'P': return "down"
                elif key in (b'\r', b'\n'): return "enter"
                elif key == b'\x03': raise KeyboardInterrupt
                else: return key.decode('utf-8', 'ignore')
            time.sleep(0.01)
else:
    import termios
    import tty
    def clear_screen():
        os.system("clear")
    
    def read_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            first = sys.stdin.read(1)
            if first == "\x1b":
                second = sys.stdin.read(1)
                third = sys.stdin.read(1)
                if third == "A": return "up"
                elif third == "B": return "down"
                return first + second + third
            if first in ("\r", "\n"):
                return "enter"
            if first == "\x03":
                raise KeyboardInterrupt
            return first
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

CONFIG_FILE = Path(__file__).with_name("configuration.py")

DEFAULT_CONFIG_CONTENT = """\
# WorkActivity Automator Settings

INITIAL_DELAY = 5
KEY_PRESS_INTERVAL = 0.3
TAB_SWITCH_DELAY = 2

# Configuration presets mapping
WORK_SETTINGS = {
    "IDE": {
        "app_duration": 300,  # total time the IDE app will be kept open (seconds)
        "tab_range": (1, 3),  # number of tabs to cycle through
        "press_range": (7, 10),  # presses per action
        "tab_duration": (60, 60),  # time each tab will be kept open (seconds)
    },
    "BROWSER": {
        "app_duration": 120,  # total time the Browser app will be kept open (seconds)
        "tab_range": (1, 4),  # number of tabs to cycle through
        "press_range": (2, 8),  # presses per action
        "tab_duration": (60, 60),  # time each tab will be kept open (seconds)
    }
}

MOUSE_CONFIG = {
    "scroll_range": (-3, 3),
    "sleep_range": (5, 10)
}
"""

def load_or_create_config():
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(DEFAULT_CONFIG_CONTENT, encoding="utf-8")
        
    try:
        spec = importlib.util.spec_from_file_location("work_config", CONFIG_FILE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"\033[91mError loading configuration file: {e}\033[0m")
        print(f"\033[93mPlease delete '{CONFIG_FILE}' and run the program again to auto-generate a new one.\033[0m")
        sys.exit(1)

keyboard = KeyboardController()
mouse = MouseController()


# --- UI Helpers ---

def print_header():
    clear_screen()
    if sys.platform.startswith("linux"):
        sys_info = f"{os.uname().sysname} {os.uname().release}"
    else:
        import platform
        sys_info = f"{platform.system()} {platform.release()}"

    print("\033[92m" + "━" * 50 + "\033[0m")
    print("\033[1;96m          WORK ACTIVITY AUTOMATOR 🚀\033[0m")
    print("\033[92m" + "━" * 50 + "\033[0m")
    print("\033[96m    💡 Stay active, look busy, take breaks!\033[0m")
    print("\033[90m    💻 System: " + sys_info + "\033[0m")
    print("\033[90m    ⚙️  Settings: configuration.py\033[0m")
    print()


def ask_boolean(prompt: str) -> bool:
    selected = True
    while True:
        print_header()
        print(f"\033[1m? {prompt} \033[90m(Y/n)\033[0m")
        print()
        if selected:
            print("  \033[92m❯ Yes\033[0m")
            print("    No")
        else:
            print("    Yes")
            print("  \033[92m❯ No\033[0m")
        
        print("\n\033[90m[Use ^/v arrows to select, Enter to confirm]\033[0m")
        
        key = read_key()
        if key in ("up", "down"):
            selected = not selected
        elif key == "enter":
            return selected


def ask_list(prompt: str, options: list) -> str:
    idx = 0
    while True:
        print_header()
        print(f"\033[1m? {prompt}\033[0m")
        print()
        for i, opt in enumerate(options):
            if i == idx:
                print(f"  \033[92m❯ {opt}\033[0m")
            else:
                print(f"    {opt}")
                
        print("\n\033[90m[Use ^/v arrows to select, Enter to confirm]\033[0m")
        
        key = read_key()
        if key == "up":
            idx = (idx - 1) % len(options)
        elif key == "down":
            idx = (idx + 1) % len(options)
        elif key == "enter":
            return options[idx]


def countdown_timer(seconds: int, message: str = "Starting in"):
    """Display a live countdown timer that updates every second."""
    for remaining in range(seconds, 0, -1):
        sys.stdout.write(f"\r\033[K{message} \033[93m{remaining}\033[0m seconds...")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write(f"\r\033[K")
    sys.stdout.flush()


def print_selection_summary(config, do_browser, do_ide, do_mouse):
    print_header()
    print("\n\033[1;96mReview your selected automation settings:\033[0m\n")
    
    if do_ide:
        ide_settings = config.WORK_SETTINGS['IDE']
        print(f"  IDE automation: \033[92mYes\033[0m")
        print(f"    - App duration: \033[93m{ide_settings['app_duration']}s\033[0m")
        print(f"    - Tab range: \033[93m{ide_settings['tab_range']}\033[0m")
        print(f"    - Press range: \033[93m{ide_settings['press_range']}\033[0m")
        print(f"    - Tab duration: \033[93m{ide_settings['tab_duration']}\033[0m")

    if do_browser:
        browser_settings = config.WORK_SETTINGS['BROWSER']
        print(f"  Browser automation: \033[92mYes\033[0m")
        print(f"    - App duration: \033[93m{browser_settings['app_duration']}s\033[0m")
        print(f"    - Tab range: \033[93m{browser_settings['tab_range']}\033[0m")
        print(f"    - Press range: \033[93m{browser_settings['press_range']}\033[0m")
        print(f"    - Tab duration: \033[93m{browser_settings['tab_duration']}\033[0m")

    if do_mouse:
        print(f"  Mouse automation: \033[92mYes\033[0m")
        print(f"    - Scroll range: \033[93m{config.MOUSE_CONFIG['scroll_range']}\033[0m")
        print(f"    - Sleep range: \033[93m{config.MOUSE_CONFIG['sleep_range']}\033[0m")

    print("\n\033[90mPress Enter to begin...\033[0m")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\n\033[91mSetup canceled by user. Goodbye.\033[0m")
        sys.exit(0)


# --- Background Mouse Thread ---

class MouseWorker(threading.Thread):
    def __init__(self, config):
        super().__init__(daemon=True)
        self.config = config
        self.running = True
        
    def run(self):
        sl_min, sl_max = self.config.MOUSE_CONFIG["sleep_range"]
        time.sleep(self.config.INITIAL_DELAY)
        
        while self.running:
            wait_time = random.randint(int(sl_min), int(sl_max))
            for remaining in range(wait_time, 0, -1):
                sys.stdout.write(f"\r\033[K   \033[93mMOUSE WAIT:\033[0m {remaining}s until next scroll...")
                sys.stdout.flush()
                time.sleep(1)

            steps = random.randint(-2, 2)
            if steps != 0:
                mouse.scroll(0, steps)

            sys.stdout.write(f"\r\033[K   \033[92mMOUSE ACTION:\033[0m Scrolled {steps:+d}\n")
            sys.stdout.flush()


# --- Action Logic ---

def execute_just_keep_active():
    print("\n\033[92m✓\033[0m Mode: \033[1mJust keep active\033[0m")
    print("Expected outcome: \033[96m2 presses / min\033[0m")
    print("Press Ctrl+C to abort.")
    countdown_timer(3, "Starting in")
    
    round_no = 1
    while True:
        sys.stdout.write(f"\r\033[K\033[36m❖ Round {round_no}:\033[0m Pressing DOWN and UP... ")
        sys.stdout.flush()
        
        keyboard.press(Key.down)
        time.sleep(0.05)
        keyboard.release(Key.down)
        time.sleep(0.5)
        keyboard.press(Key.up)
        time.sleep(0.05)
        keyboard.release(Key.up)
        
        print("\033[92m✓ Done\033[0m")
        countdown_timer(60, "Waiting")
        print(f"\033[36m❖ Round {round_no} Completed\033[0m\n")
        round_no += 1


def calculate_metrics(settings) -> float:
    p_min, p_max = settings["press_range"]
    w_min, w_max = settings["tab_duration"]
    avg_press = (p_min + p_max) / 2
    avg_wait = (w_min + w_max) / 2
    
    # keys per minute
    if avg_wait == 0: avg_wait = 1
    cycle_time = avg_wait + (avg_press * 0.3)
    cycles_per_min = 60 / cycle_time
    keys_per_min = cycles_per_min * avg_press
    return keys_per_min


def run_app_session(app_name, interval, settings):
    duration = settings["app_duration"]
    t_min, t_max = settings["tab_range"]
    w_min, w_max = settings["tab_duration"]
    p_min, p_max = settings["press_range"]
    
    started_at = time.monotonic()
    tab_index = 0
    tabs = random.randint(t_min, t_max)
    
    while time.monotonic() - started_at < duration:
        if tab_index >= tabs:
            tabs = random.randint(t_min, t_max)
            tab_index = 0

        tab_index += 1
        sys.stdout.write(f"\n   \033[96m[{app_name} Tab {tab_index}/{tabs}]\033[0m\n")
        sys.stdout.flush()

        wait_time = random.randint(w_min, w_max)
        for remaining in range(wait_time, 0, -1):
            sys.stdout.write(f"\r\033[K   \033[93mWAIT:\033[0m {remaining}s left until next action...")
            sys.stdout.flush()
            time.sleep(1)

        press_count = random.randint(p_min, p_max)
        sys.stdout.write("\n")
        sys.stdout.write(f"   \033[92mACTION:\033[0m Pressing DOWN {press_count}x\n")
        sys.stdout.flush()

        for _ in range(press_count):
            keyboard.press(Key.down)
            time.sleep(0.05)
            keyboard.release(Key.down)
            time.sleep(interval)

        if time.monotonic() - started_at >= duration:
            break

        keyboard.press(Key.ctrl)
        keyboard.press(Key.home)
        time.sleep(0.1)
        keyboard.release(Key.home)
        keyboard.release(Key.ctrl)
        time.sleep(0.2)

        keyboard.press(Key.ctrl)
        keyboard.press(Key.tab)
        time.sleep(0.1)
        keyboard.release(Key.tab)
        keyboard.release(Key.ctrl)
        time.sleep(0.2)

    sys.stdout.write(f"\r\033[K   \033[90mSession complete:\033[0m {app_name} time expired.\n")
    sys.stdout.flush()


def execute_work_mode(config, do_browser, do_ide, do_mouse):
    print_header()
    
    print("\n\033[1;96mSummary Expected Outcomes:\033[0m")
    if do_ide:
        metric = calculate_metrics(config.WORK_SETTINGS["IDE"])
        print(f" - IDE: \033[96m~{metric:.1f}\033[0m actions/min")
    if do_browser:
        metric = calculate_metrics(config.WORK_SETTINGS["BROWSER"])
        print(f" - Browser: \033[96m~{metric:.1f}\033[0m actions/min")
    if do_mouse:
        print(f" - Mouse: \033[96mRandom Jitter Enabled\033[0m")
        
    countdown_timer(config.INITIAL_DELAY, "Starting in")
    
    if do_mouse:
        m_worker = MouseWorker(config)
        m_worker.start()

    if not do_ide and not do_browser:
        print("\n\033[96mMouse-only automation enabled. Press Ctrl+C to stop.\033[0m")
        while True:
            time.sleep(1)
        
    round_no = 1
    while True:
        print(f"\n\033[1;35m━━━ [ROUND {round_no}] ━━━\033[0m")
        
        if do_ide:
            settings = config.WORK_SETTINGS["IDE"]
            print(f"\033[96m💻 Running IDE session for {settings['app_duration']}s\033[0m")
            run_app_session("IDE", config.KEY_PRESS_INTERVAL, settings)

        if do_browser:
            if do_ide:
                sys.stdout.write("\n\033[K\033[90mAlt+Tab to Browser...\033[0m\n")
                keyboard.press(Key.alt)
                keyboard.press(Key.tab)
                time.sleep(0.1)
                keyboard.release(Key.tab)
                keyboard.release(Key.alt)
                time.sleep(config.TAB_SWITCH_DELAY)
                
            settings = config.WORK_SETTINGS["BROWSER"]
            print(f"\033[93m🌐 Running Browser session for {settings['app_duration']}s\033[0m")
            run_app_session("BROWSER", config.KEY_PRESS_INTERVAL, settings)
                
            if do_ide:
                sys.stdout.write("\n\033[K\033[90mAlt+Tab to IDE...\033[0m\n")
                keyboard.press(Key.alt)
                keyboard.press(Key.tab)
                time.sleep(0.1)
                keyboard.release(Key.tab)
                keyboard.release(Key.alt)
                time.sleep(config.TAB_SWITCH_DELAY)
                
        round_no += 1


def main():
    config = load_or_create_config()
    
    # Choose mode
    mode = ask_list("Select Mode:", ["✅ Just keep active (TimeDoctor)", "⚙️ Work Mode (Upwork)"])
    
    if mode == "✅ Just keep active (TimeDoctor)":
        execute_just_keep_active()
        return

    # Work Mode
    do_ide = ask_boolean("Want IDE automation?")
    do_browser = ask_boolean("Want browser automation?")
    do_mouse = ask_boolean("Want mouse automation?")
    
    if not do_ide and not do_browser and not do_mouse:
        print("\n\033[91mNo automation selected! Exiting.\033[0m")
        return

    print_selection_summary(config, do_browser, do_ide, do_mouse)
    execute_work_mode(config, do_browser, do_ide, do_mouse)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n\033[91m🛑 Interrupted. Goodbye.\033[0m")
        sys.exit(0)
