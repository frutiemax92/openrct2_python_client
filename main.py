from .openrct2.client import OpenRCT2Client
import gradio as gr

OPENRCT2_CLIENT_PORT = 7860
GRADIO_APP_PORT = 7861

def greet(name, intensity):
    return "Hello " * intensity + name + "!"

def main():
    client = OpenRCT2Client()

    # try to connect
    error = client.connect(OPENRCT2_CLIENT_PORT)
    if error != 0:
        print(f'Could not connect to OpenRCT2: the error code is {error}')
        return
    
    # launch a gradio app
    demo = gr.Interface(
        fn=greet,
        inputs=['text', 'slider'],
        outputs=['text']
    )
    demo.launch()


if __name__ == '__main__':
    main()