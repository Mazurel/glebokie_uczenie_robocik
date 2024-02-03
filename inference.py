import sys
import time
from pathlib import Path
import json

import torch
from matplotlib import pyplot as plt

from lib import communication
from lib.nn import NeuralNet
from lib.dataset import load_image_from_path, decision_into_robot_space

def forward():
    communication.move_forward()

def backward():
    communication.move_backward()

def left():
    communication.turn_left()

def right():
    communication.turn_right()

def quit():
    communication.finished = True

def main():
    nn = NeuralNet()
    nn.load_state_dict(torch.load("./robo_net.pth"))
    step = 0

    try:
        while not communication.finished:
            while True:
                print("Enter 'yes' to make decision")
                s = input()
                if s == "yes":
                    break

            # communication.download_and_save_photo(Path("./tmp.png"))
            time.sleep(0.2)
            i = torch.tensor(load_image_from_path(Path("./tmp.png")))

            plt.imshow(i)
            plt.show()

            i = torch.unsqueeze(i, 0)
            print(i.shape)
            d = nn(i)
            decision = tuple(d.detach().numpy())
            speed, turn = decision_into_robot_space(decision)

            communication.move(int(speed))
            communication.turn_wheel(int(turn))
            communication.send_command()
            time.sleep(0.6)
            communication.reset()
            communication.send_command()
    except KeyboardInterrupt:
        print("Got interrupt - quiting ...")

    communication.reset(full=True)
    communication.send_command()


if __name__ == "__main__":
    main()
