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
    "sleep_range": (5, 10)
}
