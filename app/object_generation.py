
import gradio as gr
from diffusers import StableDiffusionPipeline

from lycoris.kohya import create_network_from_weights
import os
import urllib.request
import numpy as np
from PIL import Image
from image_utils.fuzzy_flood import fuzzy_flood
from torchvision.transforms import v2
import torchvision
import torchvision.transforms as T
from PIL.ImageDraw import floodfill
import json
import gc
import torch
import shutil
from app.common import OffsetCalculator
import zipfile

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
    #os.replace(local_filename, 'models/0p3nRCT2_v6.safetensors')
    shutil.move(local_filename, os.path.relpath('models/0p3nRCT2_v6.safetensors'))

def get_model(path : str, url_path : str):
    if os.path.exists(path):
        return
    #local_filename, headers = urllib.request.urlretrieve('https://huggingface.co/frutiemax/OpenRCT2ObjectGeneration/resolve/main/0p3nRCT2_v6.safetensors?download=true', \
    local_filename, headers = urllib.request.urlretrieve(url_path, \
        reporthook=download_progress)
    shutil.move(local_filename, os.path.relpath(path))



def progress_callback(pipe, step_index, timestep, callback_kwargs):
    return callback_kwargs

def generate_image(prompt : str, negative_prompt : str, guidance : float, threshold : float, progress=gr.Progress(track_tqdm=True)):
    # cyberrealistic classic v2.1 yields good results
    # https://civitai.com/models/71185/cyberrealistic-classic?modelVersionId=270057
    #pipeline = StableDiffusionPipeline.from_pretrained('runwayml/stable-diffusion-v1-5', \
                                                        #variant='fp16', safety_checker=None, use_safetensors=True)
    pipeline = StableDiffusionPipeline.from_single_file('https://huggingface.co/cyberdelia/CyberRealisticClassic/blob/main/CyberRealisticCLASSIC_V2.1_FP16.safetensors')

    # check for the OpenRCT2 lycoris model, if it isn't there, download it
    get_model('models/0p3nRCT2_v6.safetensors', 'https://huggingface.co/frutiemax/OpenRCT2ObjectGeneration/resolve/main/0p3nRCT2_v6.safetensors?download=true')

    network, weights_sd = create_network_from_weights(1.0, 'models/0p3nRCT2_v6.safetensors', pipeline.vae, pipeline.text_encoder, pipeline.unet, for_inference=True)
    
    network.to('cuda')
    pipeline.to('cuda')
    pipeline.unet.to('cuda')
    pipeline.text_encoder.to('cuda')
    network.apply_to(pipeline.text_encoder, pipeline.unet, apply_text_encoder=True, apply_unet=True)
    network.to('cuda')
    
    progress(0, desc='Generating...')
    
    out_image = pipeline(prompt, num_inference_steps=40, guidance_scale=guidance, negative_prompt=negative_prompt, callback_on_step_end=progress_callback).images[0]

    # free up the memory
    del pipeline
    del network
    del weights_sd
    gc.collect()

    with torch.no_grad():
        torch.cuda.empty_cache()

    post_process = post_process_image(out_image, 128, threshold, 'Nearest')


    return [out_image, post_process, 128, 'Nearest']

def generate_json(object_description : str, author : str, object_type : str, object_name : str, offsets):
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
    #properties['SMALL_SCENERY_FLAG_VOFFSET_CENTRE'] = True
    properties['hasNoSupports'] = True

    json_dict['properties'] = properties
    json_dict["images"] =  [
        { "path": "images/0.png", "x": int(offsets[0][0]), "y": int(offsets[0][1]) },
        { "path": "images/1.png", "x": int(offsets[1][0]), "y": int(offsets[1][1]) },
        { "path": "images/2.png", "x": int(offsets[2][0]), "y": int(offsets[2][1]) },
        { "path": "images/3.png", "x": int(offsets[3][0]), "y": int(offsets[3][1]) }
    ]
    name = {}
    name['en-GB'] = object_description
    
    strings = {}
    strings['name'] = name

    json_dict['strings'] = strings
    return json_dict

def post_process_image(image, image_size, threshold, resample_method : str):
    # ok, now resize the image based on the choice the user made
    # 128x128 for full tile and 64x64 for quarter tile
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)
    
    r = Image.BICUBIC
    if resample_method == 'Nearest':
        r = Image.NEAREST
    
    threshold = threshold
    
    image = image.resize((image_size, image_size), resample=r)

    # replace the background with a color rct will recognize
    #image = fuzzy_flood(image, 3.0)
    image = fuzzy_flood(image, threshold)

    # now convert the image using the palette
    palette = Image.open('data/screenshot.png')
    image = image.quantize(palette=palette, dither=Image.FLOYDSTEINBERG)

    # we now need to replace the background color with zero
    upper_left = image.getpixel((0, 0))
    for y in range(image.height):
        for x in range(image.width):
            color = image.getpixel((x, y))
            if color == upper_left:
                image.putpixel((x, y), 0)
    return image

def generate_object(image, post_image, image_size, object_name : str, object_description : str, author : str, object_type : str):
    # check for the next available object file that starts with the object name
    post_image = Image.fromarray(post_image)
    image = Image.fromarray(image)

    files = os.listdir('outputs')
    files_with_name = [filename for filename in files if object_name in filename]

    index = 0
    output_folder = None
    detected = True
    while True:
        detected = False
        output_folder_name = object_name + str(index)
        detected = False
        for filename in files_with_name:
            if output_folder_name == filename:
                detected = True
                break
        if detected == False:
            break
        index = index + 1
    output_folder = os.path.join('outputs', output_folder_name)

    # cut the image into 4 images
    images = []
    offsets = []

    # load the offset calculator model
    get_model('models/offset_calculator.pth', 'https://huggingface.co/frutiemax/OpenRCT2ObjectGeneration/resolve/main/offset_calculator.pth?download=true')
    offset_model = OffsetCalculator()
    offset_model_path = os.path.relpath('models/offset_calculator.pth')
    offset_model.load_state_dict(torch.load(offset_model_path))
    offset_model.eval()

    transforms = v2.Compose([
        v2.ToImage(),
        v2.ToDtype(torch.float32, scale=True),
        v2.Resize((256, 256), torchvision.transforms.InterpolationMode.NEAREST),
        v2.Grayscale()
    ])

    coords = [(0, 0), (1, 0), (1, 1), (0, 1)]
    for x, y in coords:
            left = x * image_size / 2
            right = left + image_size / 2
            top = y * image_size / 2
            bottom = top + image_size / 2

            view = post_image.crop((left, top, right, bottom))

            # we need to cut only the pixels we want
            bbox = view.getbbox()
            view_cropped = view.crop(bbox)
            images.append(view_cropped)

            # generate an offset
            # we must use the original image for this
            left = x * 256
            right = left + 256
            top = y * 256
            bottom = top + 256

            #view = image.crop((left, top, right, bottom))

            # transform the image into grayscale
            grayscale = transforms(view)
            grayscale = torch.reshape(grayscale, (1, 1, 256, 256))

            #to_pil_image = T.ToPILImage()
            #grayscale_image = to_pil_image(grayscale)
            #grayscale_image.show()
            offset = offset_model(grayscale)

            # we need to denormalize the offset
            scale_x = 256 / view_cropped.width
            scale_y = 256 / view_cropped.height
            scale = np.minimum(scale_x, scale_y)
            scale = 1 / scale
            offsets.append(offset[0] * scale)
            

    # now that we have our images, we need to generate the object.json
    json_dict = generate_json(object_description, author, object_type, object_name, offsets)

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
    
    # finally create a compressed version
    zipfile_path = os.path.join(output_folder, f'{output_folder_name}.parkobj')
    with zipfile.ZipFile(zipfile_path, 'w') as f:
        # write the images in the images folder
        for i in range(len(images)):
            image_path = os.path.join(images_folder, f'{i}.png')
            zip_path = os.path.relpath(f'images/{i}.png')
            f.write(image_path, zip_path, compress_type=zipfile.ZIP_DEFLATED)
        
        # write the object.json
        f.write(obj_json_path, 'object.json', compress_type=zipfile.ZIP_DEFLATED)

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
            generation_output = gr.Image(interactive=True, width=256, height=256, show_download_button=False, show_label=True, label='Output')

        # ui elements for parkobj generation
        with gr.Column():
            with gr.Row():
                object_name = gr.Textbox(value='', label='Object Name', interactive=True)
            with gr.Row():
                object_description = gr.Textbox(value='', label='Object Description', interactive=True)
        with gr.Column():
            with gr.Row():
                author = gr.Textbox(value='', label='Author', interactive=True)
            with gr.Row():
                object_type = gr.Dropdown(['Quarter Tile', 'Full Tile'], label='Object Size', value='Full Tile', interactive=True)
    

    with gr.Row():
        with gr.Column():
            post_process_output = gr.Image(interactive=False, width=256, height=256, show_download_button=False, show_label=True, label='Post Process')
        
        with gr.Column():
            with gr.Row():
                post_process_size = gr.Slider(minimum=32, maximum=256, value=128, label='Image Size', \
                                              interactive=True)
            with gr.Row():
                background_threshold = gr.Slider(minimum=0.0, maximum=100.0, value=10.0, label='Background Threshold', \
                                                 interactive=True)
        
        with gr.Column():
            with gr.Row():
                resample_method = gr.Dropdown(['Nearest', 'Bicubic'], label='Resample method', value='Nearest', interactive=True)
    with gr.Row():
        park_obj_button = gr.Button('Generate object', interactive=True)
    
    generate_button.click(
        generate_image,
        inputs=[object_prompt, negative_prompt, guidance_scroll, background_threshold], \
            outputs=[generation_output, post_process_output, post_process_size, resample_method]
    )

    park_obj_button.click(
        generate_object,
        inputs=[generation_output, post_process_output, post_process_size, object_name, object_description, author, object_type]
    )

    post_process_size.release(post_process_image, inputs=[generation_output, post_process_size, background_threshold, resample_method], \
                              outputs=[post_process_output])

    background_threshold.release(post_process_image, inputs=[generation_output, post_process_size, background_threshold, resample_method], \
                              outputs=[post_process_output])
    resample_method.change(post_process_image, inputs=[generation_output, post_process_size, background_threshold, resample_method], \
                              outputs=[post_process_output])

