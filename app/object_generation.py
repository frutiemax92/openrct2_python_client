
import gradio as gr
from diffusers import StableDiffusionPipeline

from lycoris.kohya import create_network_from_weights
import os
import urllib.request
import numpy as np
from PIL import Image
from image_utils.fuzzy_flood import fuzzy_flood
from PIL.ImageDraw import floodfill
import json

def check_for_lycoris():
    # assume that if there is a file there, it's good
    return os.path.exists('models/0p3nRCT2_v6.safetensors')

def download_progress(chunk_number, maximum_size_chunks_read, total_size, download_progress=gr.Progress()):
    download_progress(chunk_number * maximum_size_chunks_read / total_size, desc='Downloading OpenRCT2 Lycoris Model')
    print(f'chunk_number={chunk_number}, maximum_size_chunks_read={maximum_size_chunks_read}, total_size={total_size}')

def download_lycoris():
    # download the lycoris
    local_filename, headers = urllib.request.urlretrieve('https://huggingface.co/frutiemax/OpenRCT2ObjectGeneration/resolve/main/0p3nRCT2_v6.safetensors?download=true', \
                                                         reporthook=download_progress)

    # copy the file into the models folder
    os.replace(local_filename, 'models/0p3nRCT2_v6.safetensors')


def progress_callback(pipe, step_index, timestep, callback_kwargs):
    return callback_kwargs

def generate_image(prompt : str, negative_prompt : str, guidance : float, progress=gr.Progress(track_tqdm=True)):
    # cyberrealistic classic v2.1 yields good results
    # https://civitai.com/models/71185/cyberrealistic-classic?modelVersionId=270057
    #pipeline = StableDiffusionPipeline.from_pretrained('runwayml/stable-diffusion-v1-5', \
                                                        #variant='fp16', safety_checker=None, use_safetensors=True)
    pipeline = StableDiffusionPipeline.from_single_file('https://huggingface.co/cyberdelia/CyberRealisticClassic/blob/main/CyberRealisticCLASSIC_V2.1_FP16.safetensors')

    # check for the OpenRCT2 lycoris model, if it isn't there, download it
    if check_for_lycoris() == False:
        download_lycoris()

    network, weights_sd = create_network_from_weights(1.0, 'models/0p3nRCT2_v6.safetensors', pipeline.vae, pipeline.text_encoder, pipeline.unet, for_inference=True)

    network.to('cuda')
    pipeline.to('cuda')
    pipeline.unet.to('cuda')
    pipeline.text_encoder.to('cuda')
    network.apply_to(pipeline.text_encoder, pipeline.unet, apply_text_encoder=True, apply_unet=True)
    network.to('cuda')
    
    progress(0, desc='Generating...')
    return pipeline(prompt, num_inference_steps=40, guidance_scale=guidance, negative_prompt=negative_prompt, callback_on_step_end=progress_callback, callback_kwargs=progress).images[0]

def generate_json(object_description : str, author : str, object_type : str, object_name : str):
    json_dict = {}
    json_dict['id'] = object_name
    json_dict['authors'] = [author]
    
    json_dict['version'] = '1.0'
    json_dict['sourceGame'] = 'custom'
    json_dict['objectType'] = 'scenery_small'

    properties = {}
    properties['price'] = 24
    properties['removalPrice'] = -18
    properties['cursor'] = 'CURSOR_STATUE_DOWN'
    properties['height'] = 40
    
    if object_type == 'Quarter Tile':
        properties['shape'] = '1/4'
    else:
        properties['shape'] = '4/4'
    
    properties['requiresFlatSurface'] = False
    properties['isRotatable'] = True
    properties['isStackable'] = True

    json_dict['properties'] = properties
    json_dict["images"] =  [
        { "path": "images/0.png", "x": -23, "y": -42 },
        { "path": "images/1.png", "x": -23, "y": -48 },
        { "path": "images/2.png", "x": -22, "y": -48 },
        { "path": "images/3.png", "x": -22, "y": -42 }
    ]
    name = {}
    name['en-GB'] = object_description
    
    strings = {}
    strings['name'] = name

    json_dict['strings'] = strings
    return json_dict

def generate_object(image, object_name : str, object_description : str, author : str, object_type : str):
    # first check that the image is not null
    if isinstance(image, np.ndarray) == False:
        print('Error : you must generate an image before generating an object file!')
        return
    
    # check for the next available object file that starts with the object name
    files = os.listdir('outputs')
    files_with_name = [filename for filename in files if object_name in filename]

    index = 0
    output_folder = None
    detected = True
    while True:
        detected = False
        output_folder = object_name + str(index)
        detected = False
        for filename in files_with_name:
            if output_folder == filename:
                detected = True
                break
        if detected == False:
            break
        index = index + 1
    output_folder = os.path.join('outputs', output_folder)

    # ok, now resize the image based on the choice the user made
    # 128x128 for full tile and 64x64 for quarter tile
    image = Image.fromarray(image)
    width, height = 128, 128
    if object_type == 'Quarter Tile':
        width, height = 64, 64

    image = image.resize(size=(width, height), resample=Image.NEAREST)

    # replace the background with a color rct will recognize
    upper_pixel = image.getpixel((0, 0))
    for y in range(image.height):
        for x in range(image.width):
            color = image.getpixel((x, y))
            delta = np.mean(np.asarray(color) - np.asarray(upper_pixel))
            if delta < 10.0:
                image.putpixel((x, y), (23, 35, 35))

    # now convert the image using the palette
    palette = Image.open('data/screenshot.png')
    image = image.quantize(palette=palette)
    
    # cut the image into 4 images
    images = []
    for x in range(2):
        for y in range(2):
            left = x * width / 2
            right = left + width / 2
            top = y * height / 2
            bottom = top + height / 2

            view = image.crop((left, top, right, bottom))
            images.append(view)
    

    # now that we have our images, we need to generate the object.json
    json_dict = generate_json(object_description, author, object_type, object_name)

    # create a folder
    os.mkdir(output_folder)

    # create a object.json inside the output folder
    json_string = json.dumps(json_dict, indent=4)
    obj_json_path = os.path.join(output_folder, 'object.json')
    with open(obj_json_path, 'w') as f:
        f.write(json_string)
    
    # create an images folder inside the output folder
    images_folder = os.path.join(output_folder, 'images')
    os.mkdir(images_folder)

    for i in range(len(images)):
        view = images[i]
        file_path = os.path.join(images_folder, f'{i}.png')
        view.save(file_path)
    
    print('Finished')

def register_object_generation_block(client):
    with gr.Row():
        with gr.Column():
            object_prompt = gr.Textbox(value='0p3nRCT2 image, black poplar tree, green leaves, brown trunk, black background', label='Object Prompt', \
                                    interactive=True)
        with gr.Column():
            negative_prompt = gr.Textbox(value='', label='Negative Prompt', interactive=True)
        
        with gr.Column():
            guidance_scroll = gr.Slider(value=7.0, label='Guidance', maximum=11, interactive=True)
        
        with gr.Column():
            generate_button = gr.Button('Generate')

    with gr.Row():
        with gr.Column():
            generation_output = gr.Image(interactive=False, width=256, height=256, show_download_button=False, show_label=False)

        # ui elements for parkobj generation
        with gr.Column():
            with gr.Row():
                with gr.Column():
                    object_name = gr.Textbox(value='', label='Object Name', interactive=True)
                with gr.Column():
                    object_description = gr.Textbox(value='', label='Object Description', interactive=True)
            with gr.Row():
                with gr.Column():
                    author = gr.Textbox(value='', label='Author', interactive=True)
                with gr.Column():
                    object_type = gr.Dropdown(['Quarter Tile', 'Full Tile'], label='Object Size', value='Full Tile', interactive=True)
    
    with gr.Row():
        park_obj_button = gr.Button('Generate object', interactive=True)
    
    generate_button.click(
        generate_image,
        inputs=[object_prompt, negative_prompt, guidance_scroll], outputs=generation_output
    )

    park_obj_button.click(
        generate_object,
        inputs=[generation_output, object_name, object_description, author, object_type]
    )