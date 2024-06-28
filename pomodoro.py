#!/usr/bin/env python3
"""Command Line Pomodoro method timer.
"""
import os
import sys
import time
import json
import signal
import threading
from collections import deque


_DIRNAME: str = os.path.dirname(os.path.abspath(__file__))
_USR_CONFIG: dict = dict(json.load(open(_DIRNAME + "/config.json")))
_WORK_TIME: int = _USR_CONFIG["work_time_min"]
_SHORT_BREAK_TIME: int = _USR_CONFIG["short_break_time_min"]
_LONG_BREAK_TIME: int = _USR_CONFIG["long_break_time_min"]
_NUM_WORK_SESSIONS: int = _USR_CONFIG["num_work_sessions"]
_SEC_PER_MIN: int = 60
_TIMER_THREAD_SLEEP_DURATION: float = 0.2  # seconds


# Bell sound function. Different for Windows and Unix
try:
    import playsound

    def bell():
        f = _DIRNAME + "/bell.mp3"
        playsound.playsound(f, False)

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


class BoundedBuffer:
    """Bounded Buffer i.e. Producer Consumer Queue

    For communicating between the keyboard input thread and the timer thread.
    """

    def __init__(self, capacity: int = 128):
        if capacity <= 0:
            raise ValueError("Capacity must be greater than 0")
        self._items = deque()
        self._cond = threading.Condition()
        self._capacity = capacity

    def __len__(self) -> int:
        return len(self._items)

    def read(self) -> str:
        self._cond.acquire()
        while len(self._items) == 0:
            self._cond.wait()
        item = self._items.popleft()
        self._cond.notify()
        self._cond.release()
        return item

    def write(self, item: str) -> None:
        self._cond.acquire()
        while len(self._items) == self._capacity:
            self._cond.wait()
        self._items.append(item)
        self._cond.notify()
        self._cond.release()

    def clear(self) -> None:
        self._cond.acquire()
        self._items.clear()
        self._cond.notify()
        self._cond.release()


def _clear_terminal() -> None:
    """Clear the terminal screen."""
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")


def _timer(
    interval_length: int,
    print_str_preface: str,
    interval_type: str,
    bounded_buffer: BoundedBuffer,
) -> None:
    """Prints the time elapsed in the interval and waits for the interval to end.

    Parameters
    ----------
    interval_length : int
        The length of the interval in minutes.
    print_str_preface : str
        The string to print before the time elapsed string.
    interval_type : ['work', 'short break', 'long break']
    """
    time0 = time.time()
    time1 = int(time.time() - time0)
    print("Press Enter to pause the timer.")
    sys.stdout.write(f"\r\x1b[K")  # Clear the line

    while time1 < interval_length * _SEC_PER_MIN:
        # Pause the Timer
        if len(bounded_buffer):
            paused_time = time.time()
            bounded_buffer.clear()
            _clear_terminal()
            print("\r\x1b[KTimer Paused. Press Enter to resume.")
            bounded_buffer.read()
            bounded_buffer.clear()
            _clear_terminal()
            time0 += time.time() - paused_time

        time.sleep(_TIMER_THREAD_SLEEP_DURATION)
        minutes = time1 // _SEC_PER_MIN
        seconds = time1 % _SEC_PER_MIN
        sys.stdout.write(
            f"\r{print_str_preface} | Time Total: {interval_length}:00 | Time Elapsed: {minutes:02d}:{seconds:02d}"
        )
        time1 = int(time.time() - time0)

    bell()
    sys.stdout.write(f"\r\x1b[K")  # Clear the line
    if interval_type == "work":
        print("Press Enter to Begin Break...")
    else:
        print("Press Enter to Begin Work...")
    bounded_buffer.read()
    bounded_buffer.clear()
    _clear_terminal()


def _timer_handler(bounded_buffer: BoundedBuffer) -> None:
    while 1:
        for i in range(_NUM_WORK_SESSIONS):
            _timer(_WORK_TIME, f"Work time ({i})", "work", bounded_buffer)
            if i != _NUM_WORK_SESSIONS - 1:
                _timer(
                    _SHORT_BREAK_TIME,
                    f"Short break ({i})",
                    "short break",
                    bounded_buffer,
                )

        _timer(_LONG_BREAK_TIME, "Long break", "long break", bounded_buffer)


def _user_input_handler(bounded_buffer: BoundedBuffer) -> None:
    while 1:
        res = sys.stdin.read(1)
        if res:
            bounded_buffer.write(res)


if __name__ == "__main__":
    # Import playsound sometimes prints an annoying warning message. Clear it.
    _clear_terminal()

    assert type(_WORK_TIME) == int, "Work time must be a int"
    assert type(_SHORT_BREAK_TIME) == int, "Short break time must be a int"
    assert type(_LONG_BREAK_TIME) == int, "Long break time must be a int"
    assert type(_NUM_WORK_SESSIONS) == int, "Work time must be an integer"
    assert _WORK_TIME > 0, "Work time must be greater than 0"
    assert _SHORT_BREAK_TIME > 0, "Short break time must be greater than 0"
    assert _LONG_BREAK_TIME > 0, "Long break time must be greater than 0"
    assert _NUM_WORK_SESSIONS > 0, "Number of pomodoro intervals must be greater than 0"
    assert _SHORT_BREAK_TIME < 100, "Short break time must be less than 100 minutes"
    assert _LONG_BREAK_TIME < 100, "Long break time must be less than 100 minutes"

    # Handle Ctrl+C
    def sigint_handler(sig, frame):
        print('')
        sys.exit(0)
    signal.signal(signal.SIGINT, sigint_handler)

    bb = BoundedBuffer()
    t1 = threading.Thread(target=_user_input_handler, args=(bb,), daemon=True)
    t2 = threading.Thread(target=_timer_handler, args=(bb,), daemon=True)
    t1.start()
    t2.start()
    t2.join()
    t1.join()
