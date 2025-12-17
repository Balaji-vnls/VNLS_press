import torch
import torch.nn as nn
from transformers import BertModel
import torch.optim as optim
import joblib
import os
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split

# ✅ Multi-task model
# mtl_model.py

class MultiTaskNewsModel(nn.Module):
    def __init__(self, input_dim=768):
        super(MultiTaskNewsModel, self).__init__()
        self.shared_dropout = nn.Dropout(0.3)
        self.click_head = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )
        self.dwell_head = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )

    def forward(self, x):
        x = self.shared_dropout(x)
        click_out = self.click_head(x)
        dwell_out = self.dwell_head(x)
        return click_out, dwell_out


# ✅ Load precomputed data
X = torch.tensor(joblib.load("X_inputs.pkl"), dtype=torch.float32)
y_click = torch.tensor(joblib.load("y_click_labels.pkl"), dtype=torch.float32)
y_dwell = torch.tensor(joblib.load("y_relevance_labels.pkl"), dtype=torch.float32)

# ✅ Train-test split
X_train, X_test, y_click_train, y_click_test, y_dwell_train, y_dwell_test = train_test_split(
    X, y_click, y_dwell, test_size=0.2, random_state=42
)

# ✅ DataLoader
train_dataset = TensorDataset(X_train, y_click_train, y_dwell_train)
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)

# ✅ Device setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = MultiTaskNewsModel().to(device)

# ✅ Losses and optimizer
criterion_click = nn.BCEWithLogitsLoss()
criterion_dwell = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=1e-4)

# ✅ Training loop
epochs = 5
print("🚀 Training started...")

for epoch in range(epochs):
    model.train()
    total_loss = 0
    total_click_loss = 0
    total_dwell_loss = 0

    for x_batch, y_click_batch, y_dwell_batch in train_loader:
        x_batch = x_batch.to(device)
        y_click_batch = y_click_batch.unsqueeze(1).to(device)
        y_dwell_batch = y_dwell_batch.unsqueeze(1).to(device)

        optimizer.zero_grad()
        out_click, out_dwell = model(x_batch)

        loss_click = criterion_click(out_click, y_click_batch)
        loss_dwell = criterion_dwell(out_dwell, y_dwell_batch)
        loss = loss_click + loss_dwell

        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        total_click_loss += loss_click.item()
        total_dwell_loss += loss_dwell.item()

    print(f"✅ Epoch {epoch+1}/{epochs} | Total Loss: {total_loss:.4f} | Click Loss: {total_click_loss:.4f} | Dwell Loss: {total_dwell_loss:.4f}")

# ✅ Save model
os.makedirs("model", exist_ok=True)
torch.save(model.state_dict(), os.path.join("model", "mtl_model.pt"))
print("✅ Model saved to model/mtl_model.pt")
