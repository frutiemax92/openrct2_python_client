
import socket
import json
from openrct2.command_reader import *

class OpenRCT2Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, port=7860) -> int:
        return self.socket.connect(('127.0.0.1', port))
    
    def read_all(self):
        res = bytearray()
        packet = b''
        while not b'END' in res[-5:]:
            packet = self.socket.recv(1024)
            res.extend(packet)

        string_result = res[:-3].decode()
        return string_result
    
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
    
    def command_read_identifiers_from_objects(self, args):
        command = {}
        command['type'] = 'read_identifiers_from_objects'

        object_type = args
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
    
    def command_read_flags_from_object(self, args):
        command = {}

        object_id, object_type = args
        command['type'] = 'read_flags_from_object'
        command['object_id'] = object_id
        command['object_type'] = object_type
        return command

    def command_read_offsets_from_object(self, args):
        command = {}

        object_id, object_type = args
        command['type'] = 'read_offsets_from_object'
        command['object_id'] = object_id
        command['object_type'] = object_type
        return command

    def send_command(self, command_type, args) -> CommandResult:
        command = None
        if command_type == CommandTypes.READ_TILE:
            command = self.command_read_tile(args)
        elif command_type == CommandTypes.READ_IDENTIFIER_FROM_OBJECT:
            command = self.command_read_identifier_from_object(args)
        elif command_type == CommandTypes.READ_IMAGES_FROM_OBJECT:
            command = self.command_read_images_from_object(args)
        elif command_type == CommandTypes.GET_NUM_OBJECTS:
            command = self.command_get_num_objects(args)
        elif command_type == CommandTypes.READ_IDENTIFIERS_FROM_OBJECTS:
            command = self.command_read_identifiers_from_objects(args)
        elif command_type == CommandTypes.READ_FLAGS_FROM_OBJECT:
            command = self.command_read_flags_from_object(args)
        elif command_type == CommandTypes.READ_OFFSETS_FROM_OBJECT:
            command = self.command_read_offsets_from_object(args)
        
        if command == None:
            return None

        json_command = json.dumps(command)
        json_command = json_command + 'END'
        self.socket.sendall(json_command.encode())
        
        # receive the packet
        data = self.read_all()
        result = None

        if command_type == CommandTypes.READ_TILE:
            result = ReadTileResult()
        elif command_type == CommandTypes.READ_IDENTIFIER_FROM_OBJECT:
            result = ReadIdentifierFromObject()
        elif command_type == CommandTypes.READ_IMAGES_FROM_OBJECT:
            result = ReadImagesFromObjectResult()
        elif command_type == CommandTypes.GET_NUM_OBJECTS:
            result = GetNumObjectsResult()
        elif command_type == CommandTypes.READ_IDENTIFIERS_FROM_OBJECTS:
            result = ReadIdentifiersFromObject()
        elif command_type == CommandTypes.READ_FLAGS_FROM_OBJECT:
            result = ReadFlagsFromObject()
        elif command_type == CommandTypes.READ_OFFSETS_FROM_OBJECT:
            result = ReadOffsetsFromObject()
        result.parse_from_json(data)

        return result

    
