from pathlib import Path
import json
import glob
import os

os.environ["OPENCV_LOG_LEVEL"] = "SILENT"

import torch
from torch.utils.data import Dataset
import cv2
import numpy as np

from .generic import rescale
from . import communication


IMAGE_SHAPE = (64, 64)


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
        rescale(speed, (-1, 1), (-255, 255)),
        rescale(turn, (-1, 1), (communication.MAX_LEFT, communication.MAX_RIGHT)),
    )

class SubRoboDataset:
    '''
    Represents one sub dataset - one collection of photos.
    '''
    def __init__(self, path: Path) -> None:
        self.path = path

        self.image_paths = list(self.path.glob("*.png"))
        self.image_paths.sort(key=lambda p: int(p.name.split(".")[0]))

        self.decisions = json.loads((path / "decisions.json").read_text())

    def _get_decision(self, idx: int):
        speed = self.decisions["speed"][idx]
        turn = self.decisions["turn"][idx]
        return decision_into_nn_space((speed, turn))

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx: int) -> tuple[np.ndarray, torch.Tensor]:
        if idx >= len(self):
            raise IndexError("Index out of range")
        if idx < 0:
            raise IndexError("Index < 0")

        i: np.ndarray = load_image_from_path(self.image_paths[idx])
        return i, torch.tensor(np.array(self._get_decision(idx), dtype=np.float32))


class RoboDataset(Dataset):
    def __init__(self, pattern: str):
        self.subdatasets = []
        for dataset_path in glob.glob(pattern):
            self.subdatasets.append(SubRoboDataset(Path(dataset_path)))

    def __len__(self):
        return sum(map(len, self.subdatasets))

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

