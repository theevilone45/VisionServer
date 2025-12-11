import json
import argparse

# defaults
UUID = "abcd1234-1234-1234-1234-1234567890ab"
NAME = "ArduinoBL"

class Config:
    
    def __init__(self, uuid: str = UUID, 
                 device_name: str = NAME):
        self.uuid = uuid
        self.device_name = device_name
    
    @classmethod
    def from_json(cls, file_path: str) -> 'Config':
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return cls(
            uuid=data.get('uuid'),
            device_name=data.get('device_name')
        )
    
    @classmethod
    def from_args(cls) -> 'Config':
        """Load configuration from command-line arguments"""
        parser = argparse.ArgumentParser(description='Bluetooth Vision Server Configuration')
        parser.add_argument('--config-file', type=str, help='Path to JSON configuration file')
        parser.add_argument('--uuid', type=str, help='Bluetooth Service UUID')
        parser.add_argument('--device-name', type=str, help='Bluetooth Device Name')
        
        args = parser.parse_args()
        
        if args.config_file:
            config = cls.from_json(args.config_file)
            return config
        if args.uuid and args.device_name:
            config = cls(uuid=args.uuid, device_name=args.device_name)
            return config
        return cls()
    
    def __repr__(self):
        return (f"Config(uuid={self.uuid}, "
                f"device_name={self.device_name})")
