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
        "low": {
            "session_duration": 300, # 5 mins
            "tab_range": (1, 2),
            "press_range": (2, 4),
            "wait_range": (10, 20),
        },
        "high": {
            "session_duration": 600, # 10 mins
            "tab_range": (2, 5),
            "press_range": (4, 10),
            "wait_range": (3, 8),
        }
    },
    "BROWSER": {
        "low": {
            "session_duration": 60,
            "tab_range": (1, 2),
            "press_range": (1, 3),
            "wait_range": (15, 30),
        },
        "high": {
            "session_duration": 120,
            "tab_range": (2, 4),
            "press_range": (3, 6),
            "wait_range": (4, 10),
        }
    }
}

MOUSE_CONFIG = {
    "scroll_range": (-3, 3),
    "scroll_batch_range": (20, 40),
    "sleep_range": (5, 10)
}
"""

def load_or_create_config():
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(DEFAULT_CONFIG_CONTENT, encoding="utf-8")
        
    spec = importlib.util.spec_from_file_location("work_config", CONFIG_FILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

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


def print_selection_summary(config, do_browser, b_level, do_ide, i_level, do_mouse):
    print_header()
    print("\n\033[1;96mReview your selected automation settings:\033[0m\n")
    print(f"  Browser automation: \033[92m{'Yes' if do_browser else 'No'}\033[0m")
    if do_browser:
        browser_settings = config.WORK_SETTINGS['BROWSER'][b_level]
        print(f"    - Intensity: \033[96m{b_level}\033[0m")
        print(f"    - Session duration: \033[93m{browser_settings['session_duration']}s\033[0m")
        print(f"    - Press range: \033[93m{browser_settings['press_range']}\033[0m")
        print(f"    - Wait range: \033[93m{browser_settings['wait_range']}\033[0m")

    print(f"  IDE automation: \033[92m{'Yes' if do_ide else 'No'}\033[0m")
    if do_ide:
        ide_settings = config.WORK_SETTINGS['IDE'][i_level]
        print(f"    - Intensity: \033[96m{i_level}\033[0m")
        print(f"    - Session duration: \033[93m{ide_settings['session_duration']}s\033[0m")
        print(f"    - Press range: \033[93m{ide_settings['press_range']}\033[0m")
        print(f"    - Wait range: \033[93m{ide_settings['wait_range']}\033[0m")
        if i_level == 'low':
            print("    - History: This low IDE mode uses a gentler, slower automation rhythm similar to Just keep active.")

    print(f"  Mouse automation: \033[92m{'Yes' if do_mouse else 'No'}\033[0m")
    if do_mouse:
        print(f"    - Scroll jitter: \033[93m{config.MOUSE_CONFIG['scroll_range']}\033[0m")
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
        s_min, s_max = self.config.MOUSE_CONFIG["scroll_range"]
        batch_min, batch_max = self.config.MOUSE_CONFIG.get("scroll_batch_range", (20, 40))
        sl_min, sl_max = self.config.MOUSE_CONFIG["sleep_range"]
        time.sleep(self.config.INITIAL_DELAY)
        
        while self.running:
            scroll_count = random.randint(batch_min, batch_max)
            for _ in range(scroll_count):
                steps = random.randint(s_min, s_max)
                mouse.scroll(0, steps)
                time.sleep(0.01)

            sleep_time = random.uniform(sl_min, sl_max)
            sys.stdout.write(f"\033[s\033[A\033[50C\033[90m🖱️ Mouse scrolled {scroll_count}x ({s_min}..{s_max}) then slept {sleep_time:.1f}s\033[K\033[0m\033[u")
            sys.stdout.flush()
            
            time.sleep(sleep_time)


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
    w_min, w_max = settings["wait_range"]
    avg_press = (p_min + p_max) / 2
    avg_wait = (w_min + w_max) / 2
    
    # keys per minute
    if avg_wait == 0: avg_wait = 1
    cycle_time = avg_wait + (avg_press * 0.3)
    cycles_per_min = 60 / cycle_time
    keys_per_min = cycles_per_min * avg_press
    return keys_per_min


def run_tab_session(app_name, interval, settings):
    duration = settings["session_duration"]
    w_min, w_max = settings["wait_range"]
    p_min, p_max = settings["press_range"]
    
    started_at = time.monotonic()
    
    while time.monotonic() - started_at < duration:
        wait_time = random.randint(w_min, w_max)
        press_count = random.randint(p_min, p_max)
        
        # Live countdown for wait time
        for remaining in range(wait_time, 0, -1):
            sys.stdout.write(f"\r\033[K   \033[93mWAIT:\033[0m {remaining}s left until next action...")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\n")
        sys.stdout.write(f"   \033[92mACTION:\033[0m Pressing DOWN {press_count}x\n")
        sys.stdout.flush()
        
        for _ in range(press_count):
            keyboard.press(Key.down)
            time.sleep(0.05)
            keyboard.release(Key.down)
            time.sleep(interval)
            
    # Reset scroll before next tab usually
    keyboard.press(Key.ctrl)
    keyboard.press(Key.home)
    time.sleep(0.1)
    keyboard.release(Key.home)
    keyboard.release(Key.ctrl)
    time.sleep(0.2)
    
    # Switch tab
    sys.stdout.write(f"\r\033[K   \033[90mSwitching Tab...\033[0m\n")
    sys.stdout.flush()
    keyboard.press(Key.ctrl)
    keyboard.press(Key.tab)
    time.sleep(0.1)
    keyboard.release(Key.tab)
    keyboard.release(Key.ctrl)


def execute_complex_flow(config, do_browser, b_level, do_ide, i_level, do_mouse):
    print_header()
    
    print("\n\033[1;96mSummary Expected Outcomes:\033[0m")
    if do_browser:
        metric = calculate_metrics(config.WORK_SETTINGS["BROWSER"][b_level])
        print(f" - Browser \033[90m[{b_level.upper()}]\033[0m: \033[96m~{metric:.1f}\033[0m actions/min")
    if do_ide:
        metric = calculate_metrics(config.WORK_SETTINGS["IDE"][i_level])
        print(f" - IDE \033[90m[{i_level.upper()}]\033[0m:     \033[96m~{metric:.1f}\033[0m actions/min")
    if do_mouse:
        print(f" - Mouse:        \033[96mRandom Jitter Enabled\033[0m")
        
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
            settings = config.WORK_SETTINGS["IDE"][i_level]
            t_min, t_max = settings["tab_range"]
            tabs = random.randint(t_min, t_max)
            print(f"\033[96m💻 Switching to IDE\033[0m ({tabs} tabs)")
            
            for t in range(1, tabs + 1):
                sys.stdout.write(f"\n\033[96m[IDE Tab {t}/{tabs}]\033[0m\n")
                run_tab_session("IDE", config.KEY_PRESS_INTERVAL, settings)

        if do_browser:
            if do_ide:
                sys.stdout.write("\n\033[K\033[90mAlt+Tab to Browser...\033[0m\n")
                keyboard.press(Key.alt)
                keyboard.press(Key.tab)
                time.sleep(0.1)
                keyboard.release(Key.tab)
                keyboard.release(Key.alt)
                time.sleep(config.TAB_SWITCH_DELAY)
                
            settings = config.WORK_SETTINGS["BROWSER"][b_level]
            t_min, t_max = settings["tab_range"]
            tabs = random.randint(t_min, t_max)
            print(f"\033[93m🌐 Switching to Browser\033[0m ({tabs} tabs)")
            
            for t in range(1, tabs + 1):
                sys.stdout.write(f"\n\033[93m[WEB Tab {t}/{tabs}]\033[0m\n")
                run_tab_session("BROWSER", config.KEY_PRESS_INTERVAL, settings)
                
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
    
    # Onboarding
    keep_active = ask_boolean("Just keep active?")
    if keep_active:
        execute_just_keep_active()
        return

    do_browser = ask_boolean("Want browser automation?")
    b_level = None
    if do_browser:
        b_level = ask_list("Browser Intensity?", ["low", "high"])
        
    do_ide = ask_boolean("Want IDE automation?")
    i_level = None
    if do_ide:
        i_level = ask_list("IDE Intensity?", ["low", "high"])
        
    do_mouse = ask_boolean("Want mouse automation?")
    
    if not do_browser and not do_ide and not do_mouse:
        print("\n\033[91mNo automation selected! Exiting.\033[0m")
        return

    print_selection_summary(config, do_browser, b_level, do_ide, i_level, do_mouse)
    execute_complex_flow(config, do_browser, b_level, do_ide, i_level, do_mouse)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n\033[91m🛑 Interrupted. Goodbye.\033[0m")
        sys.exit(0)
