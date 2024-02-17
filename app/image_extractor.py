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

NUM_COLORS_IN_PALETTE = 12

# recolour flags for recolours
PRIMARY_COLOUR = (1 << 10)
SECONDARY_COLOUR = (1 << 19)
TERTIARY_COLOUR = (1 << 29)

# inspired by kohya_ss
def register_image_extractor_block(client : OpenRCT2Client):
    export_types = gr.CheckboxGroup(['Ride', 'Small Scenery', 'Large Scenery', 'Wall', 'Banner', 'Footpath', \
                                     'Footpath Addition', 'Scenery Group', 'Park Entrance', 'Water', 'Terrain Surface', 'Terrain Edge', \
                                        'Station', 'Music', 'Footpath Surface', 'Footpath Railings'], value=['Small Scenery', 'Large Scenery', 'Wall'], \
                                            label='Object Types', interactive=True)

    export_animated_objects = gr.Checkbox(value=False, label='Export Animated Objects')
    export_recolourable_objects = gr.Checkbox(value=False, label='Export Recolourable Objects')
    pack_images_checkbox = gr.Checkbox(value=True, label='Pack Views in 512x512 images')
    with gr.Row():
        export_path = gr.Textbox('Export Path', interactive=True, label='Export Path')
        folder_button = gr.Button(FOLDER_SYMBOL)
        export_button = gr.Button('Export')

        folder_button.click(
            get_file_path,
            outputs=export_path,
        )
        def pack_images(output_folder, image_index, pack_images : list[Image.Image]):
            num_images = len(pack_images)

            # this sucks but you need that since the objects delete the palette...
            palette = Image.open('data/screenshot.png').palette

            if num_images > 4:
                # this doesn't work for animated scenery!
                return
            
            if num_images == 1:
                image = pack_images[0]

                # get the largest side
                largest_side = np.maximum(image.width, image.height)

                # get the scaling ratio
                scaling = int(512 / largest_side)

                # scale the image
                image = image.resize((image.width * scaling, image.height * scaling))

                # copy the image into a new 512x512 centered
                new_image = Image.new(mode='P', size=(512, 512))

                # this is ok to destroy the palette after this
                new_image.palette = palette

                origin_x = int((512 - image.width) / 2)
                origin_y = int((512 - image.height) / 2)
                new_image.paste(image, (origin_x, origin_y))

                out_image = os.path.join(output_folder, f'{image_index}.png')
                new_image.save(out_image)
                image_index = image_index + 1
            elif num_images == 2:
                resized_images = []
                for image in pack_images:
                    # we need to use the smallest ratio
                    ratio_x = 256.0 / image.width
                    ratio_y = 512.0 / image.height

                    # get the scaling ratio
                    scaling = np.minimum(ratio_x, ratio_y)

                    # sometimes there are badly formed objects that exceeds the normal image size
                    scaling = np.maximum(scaling, 1.0)
                    
                    new_width = float(image.width) * scaling
                    new_width = np.round(new_width)

                    new_height = float(image.height) * scaling
                    new_height = np.round(new_height)

                    # scale the image
                    resized_images.append(image.resize((int(new_width), int(new_height))))
                
                # copy the 2 images side by side on a 512x512 image
                new_image = Image.new(mode='P', size=(512, 512))
                new_image.palette = palette

                for i in range(2):
                    origin_x = int((256 - resized_images[i].width) / 2 + 256 * i)
                    origin_y = int((512 - resized_images[i].height) / 2)
                    new_image.paste(resized_images[i], (origin_x, origin_y))

                out_image = os.path.join(output_folder, f'{image_index}.png')
                new_image.save(out_image)
                image_index = image_index + 1
            elif num_images == 4:
                resized_images = []
                for image in pack_images:
                    # we need to use the smallest ratio
                    ratio_x = 256.0 / image.width
                    ratio_y = 256.0 / image.height

                    # get the scaling ratio
                    scaling = np.minimum(ratio_x, ratio_y)

                    # sometimes there are badly formed objects that exceeds the normal image size
                    scaling = np.maximum(scaling, 1.0)

                    new_width = float(image.width) * scaling
                    new_width = np.round(new_width)

                    new_height = float(image.height) * scaling
                    new_height = np.round(new_height)

                    #print(f'width={image.width}, height={image.height}')
                    #print(f'new_width={new_width}, new_height={new_height}')

                    # scale the image
                    resized_images.append(image.resize((int(new_width), int(new_height))))

                # copy the 4 images each in its quadrant
                new_image = Image.new(mode='P', size=(512, 512))
                new_image.palette = palette

                i = 0
                for y in range(2):
                    for x in range(2):
                        origin_x = int((256 - resized_images[i].width) / 2 + 256 * x)
                        origin_y = int((256 - resized_images[i].height) / 2 + 256 * y)
                        new_image.paste(resized_images[i], (origin_x, origin_y))
                        i = i + 1

                out_image = os.path.join(output_folder, f'{image_index}.png')
                new_image.save(out_image)
                image_index = image_index + 1


            return image_index
        
        def extract_all_images_of_type(output_folder, type, exp_recolour, start_image_index = 0) -> int:
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
                # first check for the recolour flags
                read_flags_result = client.send_command(CommandTypes.READ_FLAGS_FROM_OBJECT, (j, type))
                flags = read_flags_result.flags

                # normally we shouldn't need to check for SECONDARY_COLOUR and TERTIARY_COLOUR
                if (flags & PRIMARY_COLOUR) and exp_recolour == False:
                    continue

                read_images_result = client.send_command(CommandTypes.READ_IMAGES_FROM_OBJECT, (j, type))

                # we still want the 4 views of the first frame of the animated object
                images = read_images_result.images
                if len(read_images_result.images) > 4 and export_animated_objects.value == False:
                    images = images[:4]

                # parse the images
                pckg_images = []

                # this avoid multiple copies
                copied_palette = copy(palette)

                for image in images:
                    
                    data = None
                    if image.type == 'rle':
                        data = decode_image_rle(image.data, image.width, image.height)
                    else:
                        data = np.array(image.data)
                
                    # save the image as png
                    im = Image.fromarray(data, mode='P')

                    # convert the image with the openrct2 palette
                    im.palette = copied_palette
                    
                    # save the image
                    if pack_images_checkbox.value == False:
                        out_image = os.path.join(output_path, f'{image_index}.png')
                        im.save(out_image)

                        image_index = image_index + 1
                    pckg_images.append(copy(im))
                
                if pack_images_checkbox.value == True:
                    image_index = pack_images(output_path, image_index, pckg_images)
                    # we need to pack the images in a 512x512 image
                    # there is 3 possibilities: 1 view, 2 views and 4 views object
            return image_index

        def extract_all_images(output_folder : str, exp_types, exp_recolour):
            image_index = 0
            if 'Ride' in exp_types:
                image_index = extract_all_images_of_type(output_folder, ObjectType.RIDE, exp_recolour, image_index)
            if 'Small Scenery' in exp_types:
                image_index = extract_all_images_of_type(output_folder, ObjectType.SMALL_SCENERY, exp_recolour, image_index)
            if 'Large Scenery' in exp_types:
                image_index = extract_all_images_of_type(output_folder, ObjectType.LARGE_SCENERY, exp_recolour, image_index)
            if 'Wall' in exp_types:
                image_index = extract_all_images_of_type(output_folder, ObjectType.WALL, exp_recolour, image_index)
            if 'Banner' in exp_types:
                image_index = extract_all_images_of_type(output_folder, ObjectType.BANNER, exp_recolour, image_index)
            if 'Footpath' in exp_types:
                image_index = extract_all_images_of_type(output_folder, ObjectType.FOOTPATH, exp_recolour, image_index)
            if 'Footpath Addition' in exp_types:
                image_index = extract_all_images_of_type(output_folder, ObjectType.FOOTPATH_ADDITION, exp_recolour, image_index)
            if 'Scenery Group' in exp_types:
                image_index = extract_all_images_of_type(output_folder, ObjectType.SCENERY_GROUP, exp_recolour, image_index)
            if 'Park Entrance' in exp_types:
                image_index = extract_all_images_of_type(output_folder, ObjectType.PARK_ENTRANCE, exp_recolour, image_index)
            if 'Water' in exp_types:
                image_index = extract_all_images_of_type(output_folder, ObjectType.WATER, exp_recolour, image_index)
            if 'Terrain Surface' in exp_types:
                image_index = extract_all_images_of_type(output_folder, ObjectType.TERRAIN_SURFACE, exp_recolour, image_index)
            if 'Footpath Railings' in exp_types:
                image_index = extract_all_images_of_type(output_folder, ObjectType.FOOTPATH_RAILINGS, exp_recolour, image_index)
            print('Done extracting images')

        export_button.click(
            extract_all_images,
            inputs=[export_path, export_types, export_recolourable_objects]
        )