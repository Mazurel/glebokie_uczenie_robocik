import time
from pathlib import Path

import torch
from matplotlib import pyplot as plt

from lib import communication
from lib.nn import NeuralNet
from lib.dataset import load_image_from_path, decision_into_robot_space

def main():
    nn = NeuralNet()
    nn.load_state_dict(torch.load("./robo_net.pth"))

    try:
        while True:
            while True:
                print("Enter 'y' or 'yes' to make decision")
                s = input()
                if s == "y" or s == "yes":
                    break

            time.sleep(0.2)
            communication.download_and_save_photo(Path("./tmp.png"))
            i = torch.tensor(load_image_from_path(Path("./tmp.png")))

            plt.imshow(i)
            plt.show(block=False)

            i = torch.unsqueeze(i, 0)
            d = nn(i)
            decision = tuple(d.detach().numpy())
            speed, turn = decision_into_robot_space(decision)

            print("=== Decision ===")
            print(f"Speed = {speed}")
            print(f"Turn = {turn}")

            communication.move(speed)
            communication.turn_wheel(turn)
            communication.send_command()
            time.sleep(0.9)
            communication.reset()
            communication.send_command()
    except KeyboardInterrupt:
        print("Got interrupt - quiting ...")

    communication.reset(full=True)
    communication.send_command()


if __name__ == "__main__":
    main()
