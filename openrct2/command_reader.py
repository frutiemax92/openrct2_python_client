from dataclasses import dataclass
import json
from openrct2.element import *
from openrct2.pixel_data import *

class CommandTypes:
    READ_TILE = 0
    READ_IDENTIFIER_FROM_OBJECT = 1
    READ_IMAGES_FROM_OBJECT = 2
    GET_NUM_OBJECTS = 3
    READ_IDENTIFIERS_FROM_OBJECTS = 4
    READ_FLAGS_FROM_OBJECT = 5

@dataclass
class CommandResult:
    type = None

    def parse_from_json(json_result : str):
        raise NotImplemented

@dataclass
class ReadTileResult(CommandResult):
    type = 'read_tile'
    tile_x = 0
    tile_y = 0

    elements = []

    def parse_from_json(self, json_result : str):
        json_struct = json.loads(json_result)
        self.tile_x = json_struct['tile_x']
        self.tile_y = json_struct['tile_y']

        json_elements = json_struct['elements']

        # decode each individual json element
        for json_element in json_elements:
            element = BaseTileElement()
            element.type = json_element['type']
            element.base_height = json_element['base_height']
            element.base_z = json_element['base_z']
            element.clearance_height = json_element['clearance_height']
            element.clearance_z = json_element['clearance_z']
            element.occupied_quadrants = json_element['occupied_quadrants']
            element.is_ghost = json_element['is_ghost']
            element.is_hidden = json_element['is_hidden']
            element.owner = json_element['owner']

            res_element = element
            if element.type == TileElementType.SURFACE:
                surface_element = SurfaceElement()
                surface_element.clone(element)

                surface_element.slope = json_element['slope']
                surface_element.surface_style = json_element['surface_style']
                surface_element.edge_style = json_element['edge_style']
                surface_element.water_height = json_element['water_height']
                surface_element.grass_length = json_element['grass_length']
                surface_element.ownership = json_element['ownership']
                surface_element.park_fences = json_element['park_fences']
                surface_element.has_ownership = json_element['has_ownership']
                surface_element.has_contruction_rights = json_element['has_construction_rights']
                res_element = surface_element

            elif element.type == TileElementType.FOOTPATH:
                footpath_element = FootpathElement()
                footpath_element.clone(element)

                footpath_element.object = json_element['object']
                footpath_element.surface_object = json_element['surface_object']
                footpath_element.railing_object = json_element['railings_object']
                footpath_element.edges = json_element['edges']
                footpath_element.corners = json_element['corners']
                footpath_element.slope_direction = json_element['slope_direction']
                footpath_element.is_blocked_by_vehicle = json_element['is_blocked_by_vehicle']
                footpath_element.is_wide = json_element['is_wide']
                footpath_element.is_queue = json_element['is_queue']
                footpath_element.queue_banner_direction = json_element['queue_banner_direction']
                footpath_element.ride = json_element['ride']
                footpath_element.station = json_element['station']
                footpath_element.addition = json_element['addition']
                footpath_element.addition_status = json_element['addition_status']
                footpath_element.is_addition_broken = json_element['is_addition_broken']
                footpath_element.is_addition_ghost = json_element['is_addition_ghost']
                res_element = footpath_element
            
            elif element.type == TileElementType.TRACK:
                track_element = TrackElement()
                track_element.clone(element)

                track_element.direction = json_element['direction']
                track_element.track_type = json_element['track_type']
                track_element.ride_type = json_element['ride_type']
                track_element.sequence = json_element['sequence']
                track_element.maze_entry = json_element['maze_entry']
                track_element.colour_scheme = json_element['colour_scheme']
                track_element.seat_rotation = json_element['seat_rotation']
                track_element.ride = json_element['ride']
                track_element.station = json_element['station']
                track_element.brake_booster_speed = json_element['brake_booster_speed']
                track_element.has_chain_lift = json_element['has_chain_lift']
                track_element.is_inverted = json_element['is_inverted']
                track_element.has_cable_lift = json_element['has_cable_lift']
                track_element.is_highlighted = json_element['is_highlighted']
                res_element = track_element
            
            elif element.type == TileElementType.SMALL_SCENERY:
                small_scenery_element = SmallSceneryElement()
                small_scenery_element.clone(element)

                small_scenery_element.direction = json_element['direction']
                small_scenery_element.object = json_element['object']
                small_scenery_element.primary_colour = json_element['primary_colour']
                small_scenery_element.secondary_colour = json_element['secondary_colour']
                small_scenery_element.quadrant = json_element['quadrant']
                small_scenery_element.age = json_element['age']
                res_element = small_scenery_element
            
            elif element.type == TileElementType.WALL:
                wall_element = WallElement()
                wall_element.clone(element)

                wall_element.direction = json_element['direction']
                wall_element.object = json_element['object']
                wall_element.primary_colour = json_element['primary_colour']
                wall_element.secondary_colour = json_element['secondary_colour']
                wall_element.tertiary_colour = json_element['tertiary_colour']
                wall_element.banner_index = json_element['banner_index']
                wall_element.slope = json_element['slope']
                res_element = wall_element

            elif element.type == TileElementType.ENTRANCE:
                entrance_element = EntranceElement()
                entrance_element.clone(element)

                entrance_element.direction = json_element['direction']
                entrance_element.object = json_element['object']
                entrance_element.ride = json_element['ride']
                entrance_element.station = json_element['station']
                entrance_element.sequence = json_element['sequence']
                entrance_element.footpath_object = json_element['footpath_object']
                entrance_element.footpath_surface_object = json_element['footpath_surface_object']
                res_element = entrance_element
            
            elif element.type == TileElementType.LARGE_SCENERY:
                large_scenery_element = LargeSceneryElement()
                large_scenery_element.clone(element)

                large_scenery_element.direction = json_element['direction']
                large_scenery_element.object = json_element['object']
                large_scenery_element.primary_colour = json_element['primary_colour']
                large_scenery_element.secondary_colour = json_element['secondary_colour']
                large_scenery_element.tertiary_colour = json_element['tertiary_colour']
                large_scenery_element.banner_index = json_element['banner_index']
                large_scenery_element.sequence = json_element['sequence']
                res_element = large_scenery_element
            
            elif element.type == TileElementType.BANNER:
                banner_element = BannerElement()
                banner_element.clone(element)

                banner_element.direction = json_element['direction']
                banner_element.banner_index = json_element['banner_index']
                res_element = banner_element
                
            self.elements.append(res_element)
    
@dataclass
class GetNumObjectsResult(CommandResult):
    type = 'get_num_objects'
    object_type = 0
    num_objects = 0

    def parse_from_json(self, json_result: str):
        json_struct = json.loads(json_result)
        self.object_type = json_struct['object_type']
        self.num_objects = json_struct['num_objects']

@dataclass
class ReadImagesFromObjectResult(CommandResult):
    type = 'read_images_from_object'
    object_id = None
    object_type = None
    images = []

    def parse_from_json(self, json_result: str):
        self.images = []
        self.object_type = None
        self.object_id = None
        try:
            json_struct = json.loads(json_result)
        except json.decoder.JSONDecodeError:
            return None
    
        self.object_type = json_struct['object_type']
        self.object_id = json_struct['object_id']

        json_images = json_struct['images']
        for json_image in json_images:
            pixel_data = None
            pixel_data_type = json_image['type']

            if pixel_data_type == 'raw':
                pixel_data = RawPixelData()
                pixel_data.width = json_image['width']
                pixel_data.height = json_image['height']

                if 'stride' in json_image:
                    pixel_data.stride = json_image['stride']

                # prob won't work???
                pixel_data.data = bytearray(json_image['data'].values())

            elif pixel_data_type == 'rle':
                pixel_data = RlePixelData()
                pixel_data.width = json_image['width']
                pixel_data.height = json_image['height']

                # same here
                pixel_data.data = bytearray(json_image['data'].values())
            
            else:
                pixel_data = PngPixelData()

                if 'palette' in json_image:
                    pixel_data.palette = json_image['palette']
                pixel_data.data = bytearray(json_image['data'].values())

            self.images.append(pixel_data)

@dataclass
class ReadIdentifierFromObject(CommandResult):
    type = 'read_identifier_from_object'
    object_type = None
    path = None

    def parse_from_json(self, json_result : str):
        json_struct = json.loads(json_result)
        self.object_type - json_struct['object_type']
        self.path = json_struct['path']

@dataclass
class ReadIdentifiersFromObject(CommandResult):
    type = 'read_identifiers_from_objects'
    ids = None

    def parse_from_json(self, json_result: str):
        json_struct = json.loads(json_result)
        self.ids = json_struct['ids']

@dataclass
class ReadFlagsFromObject(CommandResult):
    type = 'read_flags_from_object'
    flags = None

    def parse_from_json(self, json_result: str):
        json_struct = json.loads(json_result)

        # sometimes this fails...
        if 'flags' in json_struct:
            self.flags = json_struct['flags']