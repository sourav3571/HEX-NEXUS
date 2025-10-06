import torch
import torch.nn as nn
import torch.optim as optim
from model import SimpleCNN
from utils import dataloader, dataset
import os

BASE_DIR = os.path.dirname(__file__)
SAVE_DIR = os.path.join(BASE_DIR, "saved")

device = "cuda" if torch.cuda.is_available() else "cpu"
model = SimpleCNN(num_classes=len(dataset.classes)).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

for epoch in range(10):
    for inputs, labels in dataloader:
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
    print(f"Epoch {epoch+1}, Loss: {loss.item():.4f}")


os.makedirs(SAVE_DIR, exist_ok=True)
save_path = os.path.join(SAVE_DIR, "simplecnn.pth")
torch.save(model.state_dict(), save_path)
print(f"Model saved at {save_path}")