import numpy as np

class BinaryReader:
    def __init__(self, data : bytearray):
        self.data = data
        self.offset = 0
    
    def read_uint16(self) -> np.uint16:
        res = np.uint16()
        res = np.uint16(self.data[self.offset]) + (np.uint16(self.data[self.offset + 1]) << 8)
        self.offset = self.offset + 2
        return res
    
    def read_uint8(self) -> np.uint8:
        res = np.uint8(self.data[self.offset])
        self.offset = self.offset + 1
        return res
    
    def move_to(self, offset):
        self.offset = offset
    

def decode_image_rle(rle_data : bytearray, image_width : np.uint8, image_height : np.uint8) -> np.array:
    output = np.zeros((image_height, image_width), dtype=np.uint8)
    row_offsets = np.zeros(image_height, dtype=np.uint16)
    reader = BinaryReader(rle_data)

    for j in range(image_height):
        row_offsets[j] = reader.read_uint16()
    
    for j in range(image_height):
        reader.move_to(row_offsets[j])
        b1 = 0
        b2 = 0

        while ((b1 & 0x80) == 0):
            b1 = reader.read_uint8()
            b2 = reader.read_uint8()

            k = 0
            while k < (b1 & 0x7F):
                b3 = reader.read_uint8()
                x = b2 + k
                y = j
                output[y, x] = b3
                k = k + 1
    return output