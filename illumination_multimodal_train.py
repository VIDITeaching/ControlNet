from share import *

import sys
import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint
from torch.utils.data import DataLoader
from illumination_dataset import IlluminationMultimodalDataset
from cldm.logger import ImageLogger
from cldm.model import create_model, load_state_dict

# Configs
base_checkpoint = './models/control_sd15_ini.ckpt'
resume_checkpoint = sys.argv[1] if len(sys.argv) > 1 else None
n_epochs = 200
batch_size = 8
logger_freq = 300
checkpoint_freq = 10
learning_rate = 1e-5
sd_locked = True
only_mid_control = False


# First use cpu to load models. Pytorch Lightning will automatically move it to GPUs.
model = create_model('./models/cldm_v15.yaml').cpu()
model.load_state_dict(load_state_dict(base_checkpoint, location='cpu'))
model.learning_rate = learning_rate
model.sd_locked = sd_locked
model.only_mid_control = only_mid_control


# Misc
dataset = IlluminationMultimodalDataset()
dataloader = DataLoader(dataset, num_workers=88, batch_size=batch_size, shuffle=True)
logger = ImageLogger(batch_frequency=logger_freq)
checkpoints = ModelCheckpoint(monitor='epoch',
                              save_top_k=-1,
                              every_n_epochs=checkpoint_freq)
trainer = pl.Trainer(gpus=1, precision=32, max_epochs=n_epochs, callbacks=[logger, checkpoints], resume_from_checkpoint=resume_checkpoint)


# Train!
trainer.fit(model, dataloader)