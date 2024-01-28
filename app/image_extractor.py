from openrct2.client import OpenRCT2Client
import gradio as gr
from app.common_gui import get_file_path

FOLDER_SYMBOL = '\U0001f4c2'

# inspired by kohya_ss
def register_image_extractor_block(client : OpenRCT2Client):
    label = gr.Label('Extract Images', scale=1, )
    with gr.Row():
        export_path = gr.Textbox('Export Path', interactive=True)
        folder_button = gr.Button(FOLDER_SYMBOL)
        gr.Button('Export')


        folder_button.click(
            get_file_path,
            outputs=export_path,
        )

