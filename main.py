from openrct2.client import OpenRCT2Client
import gradio as gr
from app.image_extractor import register_image_extractor_block
from app.object_generation import register_object_generation_block
from app.train_offset_calculator import register_train_offset_calculator_block
import tkinter as tk

def greet(name):
    return "Hello " + name + "!"

def main():
    client = OpenRCT2Client()
    
    # launch a gradio app
    with gr.Blocks(title='OpenRCT2 AI Tools') as interface:
        # create some tabs
        with gr.Tab("Object Generation"):
            register_object_generation_block(client)
        with gr.Tab("Foliage Autocompleter"):
            pass
        with gr.Tab("Utilities"):
            with gr.Tab("Images extraction"):
                register_image_extractor_block(client)
            with gr.Tab("Train Offset Calculator"):
                register_train_offset_calculator_block(client)

    interface.launch()


if __name__ == '__main__':
    main()