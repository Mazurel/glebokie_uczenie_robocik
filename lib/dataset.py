from pathlib import Path
import json
import glob
from functools import lru_cache
import math

import torch
from torch.utils.data import Dataset
from torchvision import transforms
import cv2
import numpy as np

from .generic import rescale
from . import communication


IMAGE_SHAPE = (64, 64)

_data_transforms = transforms.Compose([
    transforms.RandomVerticalFlip(),
    transforms.RandomRotation(10),
])

def load_image_from_path(path: Path):
    i: np.ndarray = cv2.imread(path.as_posix())
    i = cv2.cvtColor(i, cv2.COLOR_RGB2GRAY)
    i = cv2.resize(i, IMAGE_SHAPE)
    i = np.array(i, dtype=np.float32)
    i = i / np.max(i)
    return i

def decision_into_nn_space(decision):
    speed, turn = decision
    return (
        rescale(speed, (-255, 255), (-1, 1)),
        rescale(turn, (communication.MAX_LEFT, communication.MAX_RIGHT), (-1, 1)),
    )

def decision_into_robot_space(decision):
    speed, turn = decision
    return (
        int(rescale(speed, (-1, 1), (-255, 255))),
        int(rescale(turn, (-1, 1), (communication.MAX_LEFT, communication.MAX_RIGHT))),
    )

class SubRoboDataset:
    '''
    Represents one sub dataset - one collection of photos.
    '''
    def __init__(self, path: Path, augmentation_factor: int = 0) -> None:
        self.path = path
        self.augmentation_factor = augmentation_factor

        image_paths = list(self.path.glob("*.png"))
        image_paths.sort(key=lambda p: int(p.name.split(".")[0]))

        self.decisions = json.loads((path / "decisions.json").read_text())

        self.data_cache: list[tuple[torch.Tensor, torch.Tensor]] = []
        for i in range(len(image_paths)):
            decision = self._get_decision(i)
            s, t = (decision)
            if math.isclose(s, 0): # doesn't make sense for our NN
                continue

            image: "torch.Tensor" = torch.tensor(load_image_from_path(image_paths[i]))
            image = torch.unsqueeze(image, 0)
            decision = torch.tensor(np.array(decision, dtype=np.float32))

            self.data_cache.append(
                (image, decision)
            )

    def _get_decision(self, idx: int):
        speed = self.decisions["speed"][idx]
        turn = self.decisions["turn"][idx]
        return decision_into_nn_space((speed, turn))

    def __len__(self):
        return len(self.data_cache) * (self.augmentation_factor + 1)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        if idx >= len(self):
            raise IndexError("Index out of range")
        if idx < 0:
            raise IndexError("Index < 0")

        true_idx = idx % len(self.data_cache)
        image, decision = self.data_cache[true_idx]

        if idx > len(self.data_cache):
            image = _data_transforms(image)

        return image, decision


class RoboDataset(Dataset):
    def __init__(self, pattern: str):
        self.subdatasets = []
        for dataset_path in glob.glob(pattern):
            self.subdatasets.append(SubRoboDataset(Path(dataset_path), augmentation_factor=2))

    def __len__(self):
        return sum(map(len, self.subdatasets))

    @lru_cache(10 * 1024)
    def __getitem__(self, idx: int):
        if idx >= len(self):
            raise IndexError("Index out of range")
        if idx < 0:
            raise IndexError("Index < 0")

        dataset_i = 0
        while True:
            assert dataset_i < len(self.subdatasets)

            if idx >= len(self.subdatasets[dataset_i]):
                idx -= len(self.subdatasets[dataset_i])
                dataset_i += 1
                continue

            return self.subdatasets[dataset_i][idx]

