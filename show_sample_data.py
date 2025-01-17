import random

import torch
from matplotlib import pyplot as plt

from lib.dataset import RoboDataset

if __name__ == "__main__":
    d = RoboDataset("images*")
    i = random.randint(0, len(d) - 1)

    image, decision = d[i]
    image = torch.squeeze(image)
    plt.imshow(image)
    plt.title(f"{decision}")
    plt.show()
