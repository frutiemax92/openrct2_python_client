
import socket
import json

class CommandTypes:
    READ_TILE = 0
    READ_IDENTIFIER_FROM_OBJECT = 1
    READ_IMAGES_FROM_OBJECT = 2

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

        json_command = json.dumps(command).encode()
        self.socket.sendall(json_command)
        return self.read_all()

    def command_read_identifier_from_object(self, args):
        command = {}
        command['type'] = 'read_identifier_from_object'
        
        object_id, object_type = args
        command['object_id'] = object_id
        command['object_type'] = object_type
        json_command = json.dumps(command).encode()
        self.socket.sendall(json_command)
        return self.read_all()

    def command_read_images_from_object(self, args):
        command = {}
        command['type'] = 'read_images_from_object'
        
        object_id, object_type = args
        command['object_id'] = object_id
        command['object_type'] = object_type
        json_command = json.dumps(command).encode()
        self.socket.sendall(json_command)
        return self.read_all()

    def send_command(self, command_type, args):
        res = None
        if command_type == CommandTypes.READ_TILE:
            res = self.command_read_tile(args)
        elif command_type == CommandTypes.READ_IDENTIFIER_FROM_OBJECT:
            res = self.command_read_identifier_from_object(args)
        elif command_type == CommandTypes.READ_IMAGES_FROM_OBJECT:
            res = self.command_read_images_from_object(args)
        return res

    
