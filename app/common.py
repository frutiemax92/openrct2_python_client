from tkinter import filedialog, Tk
import torch
from torch import nn

def get_file_path():
    # put the tkinter as topmost for the file dialogs
    root = Tk()
    root.wm_attributes('-topmost', 1)
    root.withdraw()

    file_path = filedialog.askdirectory()
    root.destroy()
    return file_path

# model that uses a 256x256 grayscale image input and outputs an offset xy
class OffsetCalculator(nn.Module):
    def __init__(self):
        super().__init__()

        # do convolutions until oblivion
        self.sequential_layers = nn.Sequential(
            # 256x256
            nn.Conv2d(1, 256, padding=1, dilation=1, kernel_size=6, stride=4),
            nn.ReLU(),

            # 64x64
            nn.Conv2d(256, 512, padding=1, dilation=1, kernel_size=6, stride=4),
            nn.ReLU(),

            # 16x16
            nn.Conv2d(512, 1024, padding=1, dilation=1, kernel_size=6, stride=4),
            nn.ReLU(),

            # 4x4
            nn.Flatten(),
            nn.Linear(16384, 8192),
            nn.ReLU(),
            nn.Linear(8192, 2))
    
    def forward(self, x):
        return self.sequential_layers(x)

