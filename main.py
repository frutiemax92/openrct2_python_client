from openrct2.client import OpenRCT2Client
import gradio as gr
from app.image_extractor import register_image_extractor_block
import tkinter as tk

OPENRCT2_CLIENT_PORT = 7861

def greet(name):
    return "Hello " + name + "!"

def main():
    client = OpenRCT2Client()

    # try to connect
    error = client.connect(OPENRCT2_CLIENT_PORT)
    if error != None:
        print(f'Could not connect to OpenRCT2: the error code is {error}')
        return
    
    # launch a gradio app
    with gr.Blocks() as interface:
        # create some tabs
        with gr.Tab("Object Generation"):
            pass
        with gr.Tab("Foliage Autocompleter"):
            pass
        with gr.Tab("Utilities"):
            register_image_extractor_block(client)

    interface.launch()


if __name__ == '__main__':
    main()