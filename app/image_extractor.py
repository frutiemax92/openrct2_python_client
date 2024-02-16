from openrct2.client import OpenRCT2Client
from openrct2.client import CommandTypes
from openrct2.object import ObjectType
import gradio as gr
from app.common_gui import get_file_path
from image_utils.rle_decoder import decode_image_rle

from PIL import Image
from image_utils.palette_decoder import PaletteImage
import os
import numpy as np
from copy import copy

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
            
            # first get the ride objects ids
            command_result = client.send_command(CommandTypes.GET_NUM_OBJECTS, ObjectType.SMALL_SCENERY)
            #command_result = client.send_command(CommandTypes.READ_IDENTIFIERS_FROM_OBJECTS, ObjectType.SMALL_SCENERY)

            if command_result == None:
                print('error parsing the GET_NUM_OBJECTS json in extract_all_images')
        
            num_objects = command_result.num_objects
            image_index = 0

            palette = Image.open('data/screenshot.png').palette

            for j in range(num_objects):
                read_images_result = client.send_command(CommandTypes.READ_IMAGES_FROM_OBJECT, (j, ObjectType.SMALL_SCENERY))

                # parse the images
                for image in read_images_result.images:
                    data = None
                    if image.type == 'rle':
                        data = decode_image_rle(image.data, image.width, image.height)
                    else:
                        data = np.array(image.data)
                
                    # save the image as png
                    im = Image.fromarray(data, mode='P')

                    # convert the image with the openrct2 palette
                    im.palette = copy(palette)
                    
                    # save the image
                    out_image = os.path.join(output_path, f'{image_index}.png')
                    im.save(out_image)

                    image_index = image_index + 1
                
                        
                
            
            print('Done extracting images')

        export_button.click(
            extract_all_images,
            inputs=export_path
        )