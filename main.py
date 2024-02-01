import sys
import time
from pathlib import Path
import json

import keyboard

from lib import communication

class Keyboard:
    def __init__(self) -> None:
        self.handlers = []

    def clear_handlers(self):
        for handler in self.handlers:
            keyboard.remove_hotkey(handler)
        self.handlers = []

    def enable(self):
        self.clear_handlers()
        self.handlers = [
            keyboard.add_hotkey("up", forward),
            keyboard.add_hotkey("w", forward),
            keyboard.add_hotkey("down", backward),
            keyboard.add_hotkey("s", backward),
            keyboard.add_hotkey("left", left),
            keyboard.add_hotkey("a", left),
            keyboard.add_hotkey("right", right),
            keyboard.add_hotkey("d", right),
            keyboard.add_hotkey("q", quit),
        ]

def forward():
    communication.speed = communication.REGULAR_SPEED_FORWARD

def backward():
    communication.speed = -communication.REGULAR_SPEED_FORWARD

def left():
    communication.turn = max(communication.turn - communication.TURN_CHANGE, communication.MAX_LEFT)

def right():
    communication.turn = min(communication.turn + communication.TURN_CHANGE, communication.MAX_RIGHT)

def quit():
    communication.finished = True

def main():
    step = 0
    decisions = {
        "speed": [],
        "turn": []
    }

    i = 0
    folder = Path("images/")
    while folder.exists():
        folder = Path(f"images{i}/")
        i += 1

    folder.mkdir(parents=True)

    k = Keyboard()
    k.enable()

    print()
    print("-- ROBO DATA COLLECTOR v1 --")
    print("Press:")
    print("a / left arrow -> To turn wheels left")
    print("d / right arrow -> To turn wheels right")
    print("w / up arrow -> To go forward")
    print("s / down arrow -> To go backwards")
    print("q -> Quit")
    print()
    print(f"Images are automatically saved to {folder.absolute().as_posix()}")
    print()
    print("NOTE: It is highly recommended to turn on readonly mode in your terminal !")
    print()

    try:
        while not communication.finished:
            time.sleep(0.6)  # secons to make a decision
            if communication.send_command():
                step += 1
                communication.download_and_save_photo(folder / f"{step}.png")
                decisions["speed"].append(communication.prev_speed)
                decisions["turn"].append(communication.prev_turn)
            communication.reset()
    except InterruptedError:
        print("Got interrupt - quiting ...")

    communication.reset(full=True)
    communication.send_command()

    decisions_path = folder / "decisions.json"
    with open(decisions_path, "w") as f:
        json.dump(decisions, f)
    print(f"Saved decisions into {decisions_path.absolute().as_posix()}")

if __name__ == "__main__":
    main()
