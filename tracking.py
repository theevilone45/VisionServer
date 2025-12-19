from numpy import atan2, radians, degrees, tan
from config import Config

def calculate_intrinsics(cfg: Config) -> dict:
    """Calculate camera intrinsics based on configuration"""
    # focal_length = cfg.camera_width  # Simplified assumption
    focal_x = cfg.camera_width / (2 * tan(radians(cfg.tracking_horizontal_fov) / 2))
    focal_y = cfg.camera_height / (2 * tan(radians(cfg.tracking_vertical_fov) / 2))
    center_x = cfg.camera_width / 2
    center_y = cfg.camera_height / 2
    
    intrinsics = {
        "fx": focal_x,
        "fy": focal_y,
        "cx": center_x,
        "cy": center_y
    }
    
    return intrinsics

def calculate_offset(intrinsics: dict, target: tuple[int, int], cfg: Config) -> tuple[float, float]:
    """Calculate horizontal and vertical offset angles to the target point"""
    dx = target[0] - intrinsics["cx"]
    dy = target[1] - intrinsics["cy"]
    
    h_offset = degrees(atan2(dx, intrinsics["fx"])) 
    v_offset = degrees(atan2(dy, intrinsics["fy"])) 

    # Apply dead zone
    if abs(h_offset) < cfg.tracking_dead_zone:
        h_offset = 0.0
    if abs(v_offset) < cfg.tracking_dead_zone:
        v_offset = 0.0
    
    return h_offset, v_offset