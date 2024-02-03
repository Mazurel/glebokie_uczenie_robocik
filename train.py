import torch
import torch.optim as optim
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
import tqdm
from matplotlib import pyplot as plt

from lib.nn import NeuralNet
from lib.dataset import RoboDataset

SAVE_PATH = "./robo_net.pth"
EPOCHS = 50

if __name__ == "__main__":
    net = NeuralNet()
    dataset = RoboDataset("images*")
    criterion = nn.MSELoss()
    optimizer = optim.Adam(net.parameters(), lr=0.001)

    train, test = random_split(dataset, [0.9, 0.1])

    train_loader = DataLoader(train, batch_size=1, shuffle=True)
    test_loader = DataLoader(test, batch_size=1, shuffle=False)

    test_losses = []
    train_losses = []

    progress = tqdm.tqdm(range(EPOCHS), unit="epoch")
    for epoch in progress:  # loop over the dataset multiple times
        train_running_loss = 0.0
        test_running_loss = 0.0

        for i, data in enumerate(train_loader, 0):
            # get the inputs; data is a list of [inputs, labels]
            inputs, labels = data

            # zero the parameter gradients
            optimizer.zero_grad()

            # forward + backward + optimize
            outputs = net(inputs)
            loss = criterion(outputs, labels)
            train_running_loss += loss.detach().numpy()
            loss.backward()
            optimizer.step()

        with torch.no_grad():
            for i, data in enumerate(test_loader, 0):
                # get the inputs; data is a list of [inputs, labels]
                inputs, labels = data

                # forward + backward + optimize
                outputs = net(inputs)
                loss = criterion(outputs, labels)
                test_running_loss += loss.detach().numpy()

        train_losses.append(train_running_loss)
        test_losses.append(test_running_loss)
        progress.set_description(f"Training, train_loss={train_running_loss}, val_loss={test_running_loss}")
        train_running_loss = 0.0
        test_running_loss = 0.0

    print("Finished Training")
    torch.save(net.state_dict(), SAVE_PATH)
    print(f"Saved model to {SAVE_PATH}")

    plt.plot(train_losses)
    plt.title("Train loss")
    plt.savefig("train_loss.png")

    plt.figure()
    plt.plot(test_losses)
    plt.title("Test loss")
    plt.savefig("test_loss.png")

    plt.show()
