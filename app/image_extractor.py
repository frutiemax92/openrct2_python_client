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
    export_types = gr.CheckboxGroup(['Ride', 'Small Scenery', 'Large Scenery', 'Wall', 'Banner', 'Footpath', \
                                     'Footpath Addition', 'Scenery Group', 'Park Entrance', 'Water', 'Terrain Surface', 'Terrain Edge', \
                                        'Station', 'Music', 'Footpath Surface', 'Footpath Railings'], value=['Small Scenery', 'Large Scenery', 'Wall'], \
                                            label='Object Types', interactive=True)

    export_animated_objects = gr.Checkbox(value=False, label='Export Animated Objects')
    with gr.Row():
        export_path = gr.Textbox('Export Path', interactive=True, label='Export Path')
        folder_button = gr.Button(FOLDER_SYMBOL)
        export_button = gr.Button('Export')

        folder_button.click(
            get_file_path,
            outputs=export_path,
        )

        def extract_all_images_of_type(output_folder, type, start_image_index = 0) -> int:
            # first get the ride objects ids
            output_path = os.path.abspath(output_folder)
            command_result = client.send_command(CommandTypes.GET_NUM_OBJECTS, type)
            #command_result = client.send_command(CommandTypes.READ_IDENTIFIERS_FROM_OBJECTS, ObjectType.SMALL_SCENERY)

            if command_result == None:
                print('error parsing the GET_NUM_OBJECTS json in extract_all_images')
        
            num_objects = command_result.num_objects
            image_index = start_image_index

            palette = Image.open('data/screenshot.png').palette

            for j in range(num_objects):
                read_images_result = client.send_command(CommandTypes.READ_IMAGES_FROM_OBJECT, (j, type))
                if len(read_images_result.images) > 4 and export_animated_objects.value == False:
                    continue

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
            return image_index

        def extract_all_images(output_folder : str):

            image_index = 0
            if 'Ride' in export_types.value:
                image_index = extract_all_images_of_type(output_folder, ObjectType.RIDE, image_index)
            if 'Small Scenery' in export_types.value:
                image_index = extract_all_images_of_type(output_folder, ObjectType.SMALL_SCENERY, image_index)
            if 'Large Scenery' in export_types.value:
                image_index = extract_all_images_of_type(output_folder, ObjectType.LARGE_SCENERY, image_index)
            if 'Wall' in export_types.value:
                image_index = extract_all_images_of_type(output_folder, ObjectType.WALL, image_index)
            if 'Banner' in export_types.value:
                image_index = extract_all_images_of_type(output_folder, ObjectType.BANNER, image_index)
            if 'Footpath' in export_types.value:
                image_index = extract_all_images_of_type(output_folder, ObjectType.FOOTPATH, image_index)
            if 'Footpath Addition' in export_types.value:
                image_index = extract_all_images_of_type(output_folder, ObjectType.FOOTPATH_ADDITION, image_index)
            if 'Scenery Group' in export_types.value:
                image_index = extract_all_images_of_type(output_folder, ObjectType.SCENERY_GROUP, image_index)
            if 'Park Entrance' in export_types.value:
                image_index = extract_all_images_of_type(output_folder, ObjectType.PARK_ENTRANCE, image_index)
            if 'Water' in export_types.value:
                image_index = extract_all_images_of_type(output_folder, ObjectType.WATER, image_index)
            if 'Terrain Surface' in export_types.value:
                image_index = extract_all_images_of_type(output_folder, ObjectType.TERRAIN_SURFACE, image_index)
            if 'Footpath Railings' in export_types.value:
                image_index = extract_all_images_of_type(output_folder, ObjectType.FOOTPATH_RAILINGS, image_index)
            print('Done extracting images')

        export_button.click(
            extract_all_images,
            inputs=export_path
        )