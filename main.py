import os
import requests
import keyboard
import pygame
import sys
import time

ROBOT_IP = "http://192.168.70.157"

MAX_SPEED = 250
MIN_SPEED = -250
REGULAR_SPEED_TURN = 250
REGULAR_SPEED = 180
REGULAR_SPEED_FORWARD = 140

MAX_RIGHT = 27
TURN_CHANGE = 10
MAX_LEFT = -13
STRAIGHT = 7
turn = STRAIGHT
speed = 0
prev_speed = 0
prev_turn = STRAIGHT
is_recording = False
i = 1

folder_path = r"C:\records"
save_path = r"C:\records"


def create_new_folder():
    global i, save_path
    i = 1
    # Create a new folder with a timestamp as its name
    timestamp = time.strftime("%Y%m%d%H%M%S")
    folder_name = f"Record_{timestamp}"
    new_folder_path = os.path.join(save_path, folder_name)

    try:
        os.makedirs(new_folder_path)
        return new_folder_path
    except OSError as e:
        print(f"Error creating folder: {e}")
        return None


def download_and_save_photo():
    global i, speed, turn, folder_path
    url = f"{ROBOT_IP}/photo"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            img_path = os.path.join(folder_path, f"Record_{i}_speed={speed}&turn={turn}.png")
            i += 1
            with open(img_path, 'wb') as img_file:
                img_file.write(response.content)
        else:
            print(f"Failed to download photo. Status code: {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {e}")


# Przeskalowanie wartości do obsługi pada
def rescale(value, in_min, in_max, out_min, out_max):
    return int((value - in_min) / (in_max - in_min) * (out_max - out_min) + out_min)


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


def send_command():
    global prev_speed, prev_turn
    if speed != prev_speed or turn != prev_turn:
        url = f"{ROBOT_IP}/drive?speed={speed}&turn={turn}/photo"
        requests.get(url, stream=True)
        prev_speed, prev_turn = speed, turn


def handle_keyboard():
    global speed, turn, is_recording, save_path, folder_path

    if keyboard.is_pressed("up") or keyboard.is_pressed("w"):
        if turn == STRAIGHT:
            speed = REGULAR_SPEED_FORWARD
        elif turn == MAX_RIGHT or turn == MAX_LEFT:
            speed = REGULAR_SPEED_TURN
        else:
            speed = REGULAR_SPEED
    elif keyboard.is_pressed("down") or keyboard.is_pressed("s"):
        if turn == STRAIGHT:
            speed = -REGULAR_SPEED_FORWARD
        elif turn == MAX_RIGHT or turn == MAX_LEFT:
            speed = -REGULAR_SPEED_TURN
        else:
            speed = -REGULAR_SPEED
    elif keyboard.is_pressed("t"):
        speed = MAX_SPEED
    else:
        speed = 0

    if keyboard.is_pressed("left") or keyboard.is_pressed("a"):
        turn = max(turn - TURN_CHANGE, MAX_LEFT)
    elif keyboard.is_pressed("right") or keyboard.is_pressed("d"):
        turn = min(turn + TURN_CHANGE, MAX_RIGHT)

    if keyboard.is_pressed("r"):
        is_recording = True
        print("Record started")
        folder_path = create_new_folder()
    elif keyboard.is_pressed("e"):
        is_recording = False
        print("Record stopped")


def handle_controller():
    global speed, turn, is_recording, save_path, folder_path
    for event in pygame.event.get():
        if event.type == pygame.JOYAXISMOTION:
            if event.axis == 5:  # R2 for acceleration
                update_speed(event.value, reverse=False)
            elif event.axis == 4:  # L2 for backward
                update_speed(event.value, reverse=True)
            elif event.axis == 0:  # Left stick horizontal axis for turn
                update_turn(event.value)

        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 1:  # O/B button to exit
                speed = 0
                turn = STRAIGHT
                print("Exiting program")
                pygame.quit()
                sys.exit()
            elif event.button == 0:  # X/A button
                is_recording = True
                print("Record started")
                folder_path = create_new_folder()
            elif event.button == 2:  # □/X button
                is_recording = False
                print("Record stopped")


def main():
    print(
        "Use arrow keys to control the robot. Press P/K to switch between controller and keyboard. Press 'Q' to "
        "quit.")
    CONTROLLER_MODE = 1
    KEYBOARD_MODE = 0

    try:
        pygame.init()
        pygame.joystick.init()
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        controller_detected = True
        mode = CONTROLLER_MODE
        print("Joystick detected.")
    except pygame.error:
        controller_detected = False
        print("No joystick detected. Using keyboard mode only.")
        mode = KEYBOARD_MODE

    while True:
        global speed, turn, is_recording, folder_path
        if keyboard.is_pressed("p") and controller_detected:
            mode = CONTROLLER_MODE
        elif keyboard.is_pressed("k"):
            mode = KEYBOARD_MODE

        if mode == KEYBOARD_MODE:
            handle_keyboard()
        else:
            try:
                handle_controller()
            except pygame.error:
                pass

        if keyboard.is_pressed("q"):
            speed = 0
            turn = STRAIGHT
            print("Exiting program.")
            pygame.quit()
            sys.exit()

        if is_recording and speed != 0:
            download_and_save_photo()
        time.sleep(0.1)
        send_command()
        time.sleep(0.1)


if __name__ == "__main__":
    main()
