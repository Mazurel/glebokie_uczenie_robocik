from pathlib import Path

import requests
from requests.adapters import HTTPAdapter

ROBOT_IP = "http://192.168.183.157"

MAX_SPEED = 250
MIN_SPEED = -250
REGULAR_SPEED_TURN = 250
REGULAR_SPEED = 180
REGULAR_SPEED_FORWARD = 110

MAX_RIGHT = 27
TURN_CHANGE = 10
MAX_LEFT = -13
STRAIGHT = 7

turn = STRAIGHT
speed = 0
prev_speed = 0
prev_turn = STRAIGHT
finished = False

session = requests.Session()
session.mount(ROBOT_IP, HTTPAdapter(max_retries=1))


def download_and_save_photo(file: Path):
    global speed, turn, folder_path
    url = f"{ROBOT_IP}/photo"

    if file.suffix != ".png":
        raise ValueError("Invalid file path (should have `.png` extension)")

    try:
        response = session.get(url)
        if response.status_code == 200:
            with open(file.as_posix(), 'wb') as img_file:
                img_file.write(response.content)
            print(f"Saved photo to {file.as_posix()}")
        else:
            print(f"Failed to download photo. Status code: {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {e}")


# Przeskalowanie wartości do obsługi pada
def rescale(value, in_min, in_max, out_min, out_max):
    return int((value - in_min) / (in_max - in_min) * (out_max - out_min) + out_min)

def move_forward():
    global speed
    speed = REGULAR_SPEED_FORWARD

def move_backward():
    global speed
    speed = -REGULAR_SPEED_FORWARD

def move(v: int):
    global speed
    speed = move

def turn_left():
    global turn
    turn = max(turn - TURN_CHANGE, MAX_LEFT)

def turn_right():
    global turn
    turn = min(turn + TURN_CHANGE, MAX_RIGHT)

def turn_wheel(v: int):
    global turn
    turn = v

def update_speed(value, reverse=False):
    global speed
    value = (value + 1.0) / 2.0
    if reverse:
        value = -rescale(value, 0, 1, 0, MAX_SPEED)
    else:
        value = rescale(value, 0, 1, 0, MAX_SPEED)

    speed = max(MIN_SPEED, min(MAX_SPEED, value))


def update_turn(value):
    global turn
    value = rescale(value, -1, 1, MAX_LEFT, MAX_RIGHT)

    turn = max(MAX_LEFT, min(MAX_RIGHT, value))


def send_command() -> bool:
    """Returns true when something was sent."""
    global prev_speed, prev_turn
    if speed != prev_speed or turn != prev_turn:
        print("Sending command ...")
        url = f"{ROBOT_IP}/drive?speed={speed}&turn={turn}"
        session.get(url, timeout=200)
        prev_speed, prev_turn = speed, turn
        return True
    return False

def reset(full: bool = False):
    global turn, speed
    speed = 0
    if full:
        turn = (MAX_LEFT + MAX_RIGHT) // 2
