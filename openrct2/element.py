from dataclasses import dataclass

class TileElementType:
    SURFACE = "surface"
    FOOTPATH = "footpath"
    TRACK = "track"
    SMALL_SCENERY = "small_scenery"
    WALL = "wall"
    ENTRANCE = "entrance"
    LARGE_SCENERY = "large_scenery"
    BANNER = "banner"
    NUM = 8

@dataclass
class BaseTileElement:
    type = None
    base_height = 0
    base_z = 0
    clearance_height = 0
    clearance_z = 0
    occupied_quadrants = 0
    is_ghost = 0
    is_hidden = 0
    owner = 0

@dataclass
class SurfaceElement(BaseTileElement):
    type = TileElementType.SURFACE
    slope = 0
    surface_style = 0
    edge_style = 0
    water_height = 0
    grass_length = 0
    ownership = 0
    park_fences = 0
    has_ownership = False
    has_contruction_rights = False

@dataclass
class FootpathElement(BaseTileElement):
    type = TileElementType.FOOTPATH
    object = None
    surface_object = None
    railing_object = None
    
    edges = 0
    corners = 0
    slope_direction = 0
    is_blocked_by_vehicle = False
    is_wide = False

    is_queue = False
    queue_banner_direction = None
    ride = None
    station = None

    addition = None
    addition_status = None
    is_addition_broken = None
    is_addition_ghost = None

@dataclass
class TrackElement(BaseTileElement):
    type = TileElementType.TRACK
    
    direction = 0
    track_type = 0
    ride_type = 0
    sequence = None
    maze_entry = None

    colour_scheme = None
    seat_rotation = None

    ride = 0
    station = None

    brake_booster_speed = None
    has_chain_lift = False
    is_inverted = False
    has_cable_lift = False
    is_highlighted = False

@dataclass
class SmallSceneryElement(BaseTileElement):
    type = TileElementType.SMALL_SCENERY

    direction = 0
    object = 0
    primary_colour = 0
    secondary_colour = 0
    quadrant = 0
    age = 0

@dataclass
class WallElement(BaseTileElement):
    type = TileElementType.WALL

    direction = 0
    object = 0
    primary_colour = 0
    secondary_colour = 0
    tertiary_colour = 0
    banner_index = None
    slope = 0

@dataclass
class EntranceElement(BaseTileElement):
    type = TileElementType.ENTRANCE

    direction = 0
    object = 0
    ride = 0
    station = 0
    sequence = 0
    footpath_object = None
    footpath_surface_object = None

@dataclass
class LargeSceneryElement(BaseTileElement):
    type = TileElementType.LARGE_SCENERY
    
    direction = 0
    object = 0
    primary_colour = 0
    secondary_colour = 0
    tertiary_colour = 0
    banner_index = None
    sequence = 0

@dataclass
class BannerElement(BaseTileElement):
    type = TileElementType.BANNER
    direction = 0
    banner_index = 0
