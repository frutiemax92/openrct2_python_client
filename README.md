# Summary

This projet is a set of tools that uses AI using libraries in Python.
What is currently implemented:

- Image generation using the Cyberrealistic classic v2.1 and OpenRCT2 Object Generator Lycoris
- TCP client utility that can extract all images from a savefile. You need this required plugin for it to be working : https://github.com/frutiemax92/openrct2_tcp_server

What is planned:

- Post processing of the image generation tool to generate .parkobjs
- An automatic foliage placement tool

## How to install

For windows, run setup.bash.
For Linux, run setup_linux.sh.

## Notes for the image generation tool

This tool is a very simplified version of Automatic1111 webui tool. To generate an image, type what you want to see in the object prompt and what you don't want to see in the negative prompt.

The prompt should have the keyword 0p3nRCT2 but you can experiment with it. A guidance between 5 and 9 is highly suggested.

## Notes for the Image Extraction tool

This tool can extract all images from a save file. It has been used to generate the dataset for the OpenRCT2 lycoris model. To export, it is required that you first load the park file with this plugin installed : https://github.com/frutiemax92/openrct2_tcp_server.

You can select the types of object you want to export but I only tested it with small scenery, there is some work to be done for large scenery.