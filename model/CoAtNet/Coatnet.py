import torch
import torchvision
from torch import nn
import pytorch_lightning as pl
from model.CoAtNet.CoAtNet import CoAtNet

class CoAtNetModule(pl.LightningModule):
    def __init__(self, num_classes):
        super().__init__()
        self.backbone = CoAtNet()
        self.fc = nn.Linear(768, num_classes)

    def forward(self, x):
        x = self.backbone(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x

    def training_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)
        loss = nn.CrossEntropyLoss()(logits, y)
        return {'loss': loss}

    def validation_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)
        loss = nn.CrossEntropyLoss()(logits, y)
        acc = (logits.argmax(dim=1) == y).float().mean()
        return {'val_loss': loss, 'val_acc': acc}

    def validation_epoch_end(self, outputs):
        avg_loss = torch.stack([x['val_loss'] for x in outputs]).mean()
        avg_acc = torch.stack([x['val_acc'] for x in outputs]).mean()
        self.log('val_loss', avg_loss)
        self.log('val_acc', avg_acc)

    def configure_optimizers(self):
        optimizer = torch.optim.SGD(self.parameters(), lr=0.1, momentum=0.9, weight_decay=1e-4)
        lr_scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=90)
        return {'optimizer': optimizer, 'lr_scheduler': lr_scheduler}

    def count_parameters(self):
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

# Create PyTorch Lightning Trainer and DataModule

trainer = pl.Trainer(gpus=1, max_epochs=100, progress_bar_refresh_rate=20)
data_module = torchvision.datasets.ImageNet('./', train=True, download=True)
model = CoAtNetModule(num_classes=1000)
# Initialize CoAtNetx model and train
trainer.fit(model, datamodule=data_module)
print(model.count_parameters())
