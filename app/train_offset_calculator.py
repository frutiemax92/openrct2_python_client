import gradio as gr
from app.common import get_file_path
import torch
from torch import nn
from PIL import Image
import os
from app.common import OffsetCalculator
from torch.utils.data import DataLoader
from torchvision.transforms import v2
import torchvision
from torch.utils.data import Dataset
from tqdm import tqdm
import json

class ImageOffsetDataset(Dataset):
    def __init__(self, dataset_path : str, transform):
        self.dataset_path = dataset_path
        self.transform = transform

        # get the number of images
        files = os.listdir(dataset_path)
        self.dataset_path = os.path.abspath(dataset_path)
        self.num_images = int(len(files) / 2)
    
    def __len__(self):
        return self.num_images
    
    def __getitem__(self, idx):
        image_path = os.path.join(self.dataset_path, f'{idx}.png')
        image = Image.open(image_path)
        
        #convert the image into a 256x256 grayscale
        image = self.transform(image)

        offset_path = os.path.join(self.dataset_path, f'{idx}.json')
        f = open(offset_path)
        file_string = f.read()
        json_struct = json.loads(file_string)

        offset = torch.tensor([float(json_struct['x']), float(json_struct['y'])])
        return image, offset

FOLDER_SYMBOL = '\U0001f4c2'

def train_offset_calculator(dataset_path : str, num_iterations : int, num_repeats : int, learning_rate : float, batch_size : int):
    num_repeats = int(num_repeats)
    num_iterations = int(num_iterations)
    learning_rate = float(learning_rate)
    batch_size = int(batch_size)
    # transform the images
    # we need 256x256 grayscale images
    transforms = v2.Compose([
        v2.ToImage(),
        v2.ToDtype(torch.float32, scale=True),
        v2.Resize((256, 256), torchvision.transforms.InterpolationMode.NEAREST),
        v2.Grayscale()
    ])

    dataset = ImageOffsetDataset(dataset_path, transforms)

    # put the images and offsets in a dataloader
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model = OffsetCalculator()
    loss_fn = nn.MSELoss()
    optimizer = torch.optim.AdamW(model.parameters())

    model.to('cuda')
    model.train()

    num_images = len(dataset)
    num_steps = int(num_repeats * num_iterations * num_images / batch_size)

    with tqdm(total=num_steps) as pbar:
        for iter in range(num_iterations):
            error_sum = 0
            num_sums = 0
            for batch, (X, y) in enumerate(dataloader):
                X = X.to('cuda')
                y = y.to('cuda')

                for repetition in range(num_repeats):
                    pred = model(X)
                    loss = loss_fn(pred, y)
                    loss.backward()
                    optimizer.step()
                    optimizer.zero_grad()
                    pbar.update()

                    error_sum = error_sum + loss
                    num_sums = num_sums + 1
            error_mean = error_sum / num_sums
            pbar.set_description(f'mean error={error_mean}')
            

    # save the model at the end
    output_file = os.path.relpath('models/offset_calculator.pth')
    torch.save(model.state_dict(), output_file)

    print('done training')


def register_train_offset_calculator_block(client):
    with gr.Row():
        with gr.Column():
            num_iterations_textbox = gr.Textbox(2, interactive=True, label='Number of iterations')
        with gr.Column():
            num_repeats_textbox = gr.Textbox(5, interactive=True, label='Number of repetitions')
    with gr.Row():
        with gr.Column():
            learning_rate_textbox = gr.Textbox(1e-5, interactive=True, label='Learning rate')
        with gr.Column():
            batch_size_slider = gr.Slider(minimum=1, maximum=64, value=2, label='Batch Size', interactive=True)
    with gr.Row():
        with gr.Column():
            dataset_path = gr.Textbox('Dataset Path', interactive=True, label='Dataset Path')
        with gr.Column():
            folder_button = gr.Button(FOLDER_SYMBOL)
        with gr.Column():
            train_button = gr.Button('Train')
    
    folder_button.click(
        get_file_path,
        outputs=dataset_path,
    )

    train_button.click(
        train_offset_calculator,
        inputs=[dataset_path, num_iterations_textbox, num_repeats_textbox, learning_rate_textbox, batch_size_slider]
    )