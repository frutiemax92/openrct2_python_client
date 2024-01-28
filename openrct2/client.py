
import socket
import json
from openrct2.command_reader import CommandTypes

class OpenRCT2Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, port=7860) -> int:
        return self.socket.connect(('127.0.0.1', port))
    
    def read_all(self):
        res = bytearray()
        while True:
            recv = self.socket.recv(4096)
            res.extend(recv)
            if len(recv) < 4096:
                break
        return res.decode()
    
    def command_read_tile(self, args):
        tile_x, tile_y = args
        command = {}
        command['type'] = 'read_tile'
        command['tile_x'] = tile_x
        command['tile_y'] = tile_y
        return command

    def command_read_identifier_from_object(self, args):
        command = {}
        command['type'] = 'read_identifier_from_object'
        
        object_id, object_type = args
        command['object_id'] = object_id
        command['object_type'] = object_type
        return command

    def command_read_images_from_object(self, args):
        command = {}
        command['type'] = 'read_images_from_object'
        
        object_id, object_type = args
        command['object_id'] = object_id
        command['object_type'] = object_type
        return command

    def command_get_num_objects(self, args):
        command = {}

        object_type = args
        command['type'] = 'get_num_objects'
        command['object_type'] = object_type
        return command

    def send_command(self, command_type, args):
        command = None
        if command_type == CommandTypes.READ_TILE:
            command = self.command_read_tile(args)
        elif command_type == CommandTypes.READ_IDENTIFIER_FROM_OBJECT:
            command = self.command_read_identifier_from_object(args)
        elif command_type == CommandTypes.READ_IMAGES_FROM_OBJECT:
            command = self.command_read_images_from_object(args)
        elif command_type == CommandTypes.GET_NUM_OBJECTS:
            command = self.command_get_num_objects(args)
        
        if command == None:
            return None

        json_command = json.dumps(command).encode()
        self.socket.sendall(json_command)
        return self.read_all()

    
