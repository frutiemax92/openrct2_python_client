
import gradio as gr
from diffusers import StableDiffusionPipeline

from lycoris.kohya import create_network_from_weights
import os
import urllib.request

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

def generate_object(image, object_name : str, object_description : str, author : str, object_type : str):
    pass

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
        park_obj_button = gr.Button('Generate object')
    
    generate_button.click(
        generate_image,
        inputs=[object_prompt, negative_prompt, guidance_scroll], outputs=generation_output
    )

    


