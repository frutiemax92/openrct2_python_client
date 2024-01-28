from dataclasses import dataclass
import numpy as np

@dataclass
class RawPixelData:
    type = 'raw'
    width = 0
    height = 0
    stride = 0
    data = None

@dataclass
class RlePixelData:
    type = 'rle'
    width = 0
    height = 0
    data = None

@dataclass
class PngPixelData:
    type = 'png'
    palette = None
    data = None