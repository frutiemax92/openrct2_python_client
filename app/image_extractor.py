from openrct2.client import OpenRCT2Client
from openrct2.client import CommandTypes
from openrct2.object import ObjectType
import gradio as gr
from app.common_gui import get_file_path
import os

FOLDER_SYMBOL = '\U0001f4c2'



# inspired by kohya_ss
def register_image_extractor_block(client : OpenRCT2Client):
    label = gr.Label('Extract Images', scale=1, )
    with gr.Row():
        export_path = gr.Textbox('Export Path', interactive=True)
        folder_button = gr.Button(FOLDER_SYMBOL)
        export_button = gr.Button('Export')

        folder_button.click(
            get_file_path,
            outputs=export_path,
        )

        def extract_all_images(output_folder : str):
            output_path = os.path.abspath(output_folder)
            
            # first get the ride objects
            command_result = client.send_command(CommandTypes.GET_NUM_OBJECTS, ObjectType.RIDE)

            if command_result == None:
                print('error parsing the GET_NUM_OBJECTS json in extract_all_images')
        
            num_objects = command_result.num_objects
            for j in range(num_objects):
                read_images_result = client.send_command(CommandTypes.READ_IMAGES_FROM_OBJECT, (j, ObjectType.RIDE))
            
            print('Done extracting images')

        export_button.click(
            extract_all_images,
            inputs=export_path
        )