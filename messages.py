import uuid
import json 

class ServoCommand:
    def __init__(self, servo1_offset: int = 0, servo2_offset: int = 0, msg_id: int | None = None):
        self.msg_id: int = msg_id if msg_id is not None else (int(uuid.uuid4()) & 0xFFFF)  # 16-bit ID
        self.servo1_offset = servo1_offset
        self.servo2_offset = servo2_offset

    def to_json(self) -> str:
        return json.dumps({
            "msg_id": self.msg_id,
            "s1_offset": self.servo1_offset,
            "s2_offset": self.servo2_offset
        })

    @classmethod
    def from_json(cls, data: str) -> 'ServoCommand':
        obj = json.loads(data)
        return cls(msg_id=obj['msg_id'], servo1_offset=obj['servo1_offset'], servo2_offset=obj['servo2_offset'])
    
class AckMessage:
    def __init__(self, msg_id: int, success: bool, error_msg: str = ""):
        self.msg_id = msg_id
        self.success = success
        self.error_msg = error_msg

    def to_json(self) -> str:
        return json.dumps({
            "msg_id": self.msg_id,
            "success": self.success,
            "error_msg": self.error_msg
        })

    @classmethod
    def from_json(cls, data: str) -> 'AckMessage':
        obj = json.loads(data)
        return cls(msg_id=obj['msg_id'], success=obj['success'], error_msg=obj.get('error_msg', ""))


# TODO: implement non blocking servo operation with progress
class ProgressMessage:
    def __init__(self, msg_id: int, progress: float):
        self.msg_id = msg_id
        self.progress = progress

    def to_json(self) -> str:
        return json.dumps({
            "msg_id": self.msg_id,
            "progress": self.progress
        })

    @classmethod
    def from_json(cls, data: str) -> 'ProgressMessage':
        obj = json.loads(data)
        return cls(msg_id=obj['msg_id'], progress=obj['progress'])