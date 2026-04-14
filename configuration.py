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
