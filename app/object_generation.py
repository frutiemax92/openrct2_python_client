
import gradio as gr
from diffusers import StableDiffusionPipeline
from diffusers.pipelines.auto_pipeline import AutoPipelineForText2Image
import peft

import torch
from lycoris.kohya import create_network_from_weights
import os
import urllib.request
import tqdm

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

def generate_object(prompt : str, negative_prompt : str, guidance : float, progress=gr.Progress(track_tqdm=True)):
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
    



def register_object_generation_block(client):
    with gr.Column():
        with gr.Row():
            object_prompt = gr.Textbox(value='Enter your prompt here', label='Object Prompt', interactive=True)
            negative_prompt = gr.Textbox(value='Enter your negative prompt here', label='Object Prompt', interactive=True)
            guidance_scroll = gr.Slider(value=7.0, label='Guidance', interactive=True)
            generate_button = gr.Button('Generate')
        generation_output = gr.Image(interactive=False)
    
    generate_button.click(
        generate_object,
        inputs=[object_prompt, negative_prompt, guidance_scroll], outputs=generation_output
    )


