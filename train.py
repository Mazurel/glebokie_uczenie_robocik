import torch
import torch.optim as optim
import torch.nn as nn
from torch.utils.data import DataLoader
import tqdm

from lib.nn import NeuralNet
from lib.dataset import RoboDataset

SAVE_PATH = "./robo_net.pth"

net = NeuralNet()
dataset = RoboDataset("images*")
criterion = nn.MSELoss()
optimizer = optim.Adam(net.parameters(), lr=0.001)

trainloader = DataLoader(dataset, batch_size=1, shuffle=True)

pbar = tqdm.tqdm()

losses = []

for epoch in range(20):  # loop over the dataset multiple times
    running_loss = 0.0
    for i, data in enumerate(trainloader, 0):
        # get the inputs; data is a list of [inputs, labels]
        inputs, labels = data

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        outputs = net(inputs)
        loss = criterion(outputs, labels)
        running_loss += loss
        loss.backward()
        optimizer.step()

    losses.append(running_loss)
    pbar.set_description(f"Training, loss={running_loss}")
    running_loss = 0.0
    pbar.update()

print("Finished Training")
torch.save(net.state_dict(), SAVE_PATH)
print(f"Saved model to {SAVE_PATH}")

