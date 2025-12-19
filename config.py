import json
import argparse

# defaults
UUID = "abcd1234-1234-1234-1234-1234567890ab"
NAME = "ArduinoBL"
CAMERA_WIDTH = 960
CAMERA_HEIGHT = 720
CAMERA_FORMAT = "YUV420"
CAMERA_DEBUG = True
TRACKING_DEAD_ZONE = 2
TRACKING_HORIZONTAL_FOV = 62
TRACKING_VERTICAL_FOV = 48

class Config:
    def __init__(self, uuid: str = UUID, 
                 device_name: str = NAME,
                 camera_width: int = CAMERA_WIDTH,
                 camera_height: int = CAMERA_HEIGHT,
                 camera_format: str = CAMERA_FORMAT,
                 camera_debug: bool = CAMERA_DEBUG,
                 tracking_dead_zone: int = TRACKING_DEAD_ZONE,
                 tracking_horizontal_fov: int = TRACKING_HORIZONTAL_FOV,
                 tracking_vertical_fov: int = TRACKING_VERTICAL_FOV):
        self.uuid = uuid
        self.device_name = device_name
        self.camera_width = camera_width
        self.camera_height = camera_height
        self.camera_format = camera_format
        self.camera_debug = camera_debug
        self.tracking_dead_zone = tracking_dead_zone
        self.tracking_horizontal_fov = tracking_horizontal_fov
        self.tracking_vertical_fov = tracking_vertical_fov
    
    @classmethod
    def from_json(cls, file_path: str) -> 'Config':
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return cls(
            uuid=data.get('uuid'),
            device_name=data.get('device_name'),
            camera_width=data.get('camera', {}).get('width', CAMERA_WIDTH),
            camera_height=data.get('camera', {}).get('height', CAMERA_HEIGHT),
            camera_format=data.get('camera', {}).get('format', CAMERA_FORMAT),
            camera_debug=data.get('camera', {}).get('debug', CAMERA_DEBUG),
            tracking_dead_zone=data.get('tracking', {}).get('dead_zone', TRACKING_DEAD_ZONE),
            tracking_horizontal_fov=data.get('tracking', {}).get('horizontal_fov', TRACKING_HORIZONTAL_FOV),
            tracking_vertical_fov=data.get('tracking', {}).get('vertical_fov', TRACKING_VERTICAL_FOV)
        )
    
    @classmethod
    def from_args(cls) -> 'Config':
        """Load configuration from command-line arguments"""
        parser = argparse.ArgumentParser(description='Bluetooth Vision Server Configuration')
        parser.add_argument('--config-file', type=str, help='Path to JSON configuration file')
        
        args = parser.parse_args()
        
        if args.config_file:
            return cls.from_json(args.config_file)
        
        return cls()
    
    def __repr__(self):
        return (f"Config(uuid={self.uuid}, "
                f"device_name={self.device_name})"
                f"camera_width={self.camera_width}, "
                f"camera_height={self.camera_height}, "
                f"camera_format={self.camera_format}, "
                f"camera_debug={self.camera_debug}, "
                f"tracking_dead_zone={self.tracking_dead_zone}), "
                f"tracking_horizontal_fov={self.tracking_horizontal_fov}, "
                f"tracking_vertical_fov={self.tracking_vertical_fov})")