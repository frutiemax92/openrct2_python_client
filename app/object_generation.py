
import gradio as gr
from diffusers import AutoPipelineForText2Image
from diffusers import StableDiffusionPipeline
from diffusers import StableDiffusionAdapterPipeline
from diffusers import DPMSolverMultistepScheduler
from diffusers.loaders.lora import LoraLoaderMixin
from peft import LoHaModel, LoHaConfig
import peft

import torch

def generate_object(prompt : str, negative_prompt : str, guidance : float):
    # cyberrealistic classic v2.1 yields good results
    # https://civitai.com/models/71185/cyberrealistic-classic?modelVersionId=270057
    pipeline = StableDiffusionPipeline.from_pretrained('runwayml/stable-diffusion-v1-5', \
                                                        variant='fp16', safety_checker=None, use_safetensors=True)

    # we also need to load our lycoris model
    config_te = LoHaConfig(
        r=128,
        alpha=128,
        target_modules=["k_proj", "q_proj", "v_proj", "out_proj", "fc1", "fc2"],
        rank_dropout=0.0,
        module_dropout=0.0,
        init_weights=True,
        base_model_name_or_path='models/0p3nRCT2_v6.safetensors'
    )

    config_unet = LoHaConfig(
        r=128,
        alpha=128,
        target_modules=[
            "proj_in",
            "proj_out",
            "to_k",
            "to_q",
            "to_v",
            "to_out.0",
            "ff.net.0.proj",
            "ff.net.2",
        ],
        rank_dropout=0.0,
        module_dropout=0.0,
        init_weights=True,
        use_effective_conv2d=True,
        base_model_name_or_path='models/0p3nRCT2_v6.safetensors'
    )

    lycoris_model = peft.auto.AutoPeftModel.from_pretrained('models/0p3nRCT2_v6.safetensors')


    #pipeline.text_encoder = LoHaModel(pipeline.text_encoder, config_te, 'default')
    #pipeline.unet = LoHaModel(pipeline.unet, config_unet, 'default')

    #pipeline.load_lora_weights("hf-internal-testing/edgLycorisMugler-light", weight_name="edgLycorisMugler-light.safetensors")
    pipeline.to('cuda')
    return pipeline(prompt, num_inference_steps=40, guidance_scale=guidance, negative_prompt=negative_prompt).images[0]
    



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


