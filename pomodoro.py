#!/usr/bin/env python3
"""Command Line Pomodoro method timer.
"""
import os
import sys
import time

try:
    import playsound

    def bell():
        playsound.playsound("bell.mp3", False)

except ImportError:
    playsound = None
    if sys.platform == "win32":
        import winsound

        def bell():
            winsound.Beep(523, 700)

    else:

        def bell():
            print("\a")
            os.system("clear")


# User Set Variables. Modify as needed
_WORK_TIME = 25  # min
_SHORT_BREAK_TIME = 5  # min, 3-5 min
_LONG_BREAK_TIME = 25  # min, 15-30 min every 4 pomodoro work sessions
_NUM_POMODORO_INTERVALS = 4

# Progam variables. Do not modify
_SEC_PER_MIN = 60
_PROCESS_SLEEP_DURATION = 0.2  # s


def _interval(interval_length: int, print_str_preface: str) -> None:
    time0 = time.time()
    time1 = int(time.time() - time0)
    sys.stdout.write(f"\r\x1b[K")  # Clear the line
    while time1 < interval_length * _SEC_PER_MIN:
        time.sleep(_PROCESS_SLEEP_DURATION)
        minutes = time1 // _SEC_PER_MIN
        seconds = time1 % _SEC_PER_MIN
        sys.stdout.write(
            f"\r{print_str_preface} | Time Total: {interval_length}:00 | Time Elapsed: {minutes:02d}:{seconds:02d}"
        )
        time1 = int(time.time() - time0)

    bell()


if __name__ == "__main__":
    # Import playsound sometimes prints an annoying warning message
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")

    assert _WORK_TIME > 0, "Work time must be greater than 0"
    assert _SHORT_BREAK_TIME > 0, "Short break time must be greater than 0"
    assert _LONG_BREAK_TIME > 0, "Long break time must be greater than 0"
    assert (
        _NUM_POMODORO_INTERVALS > 0
    ), "Number of pomodoro intervals must be greater than 0"
    assert type(_WORK_TIME) == int, "Work time must be a int"
    assert type(_SHORT_BREAK_TIME) == int, "Short break time must be a int"
    assert type(_LONG_BREAK_TIME) == int, "Long break time must be a int"
    assert type(_NUM_POMODORO_INTERVALS) == int, "Work time must be an integer"
    assert _SHORT_BREAK_TIME < 100, "Short break time must be less than 100 minutes"
    assert _LONG_BREAK_TIME < 100, "Long break time must be less than 100 minutes"

    while 1:
        for i in range(_NUM_POMODORO_INTERVALS):
            _interval(_WORK_TIME, f"Work time ({i})")
            if i != _NUM_POMODORO_INTERVALS - 1:
                _interval(_SHORT_BREAK_TIME, f"Short break ({i})")

        _interval(_LONG_BREAK_TIME, "Long break")
