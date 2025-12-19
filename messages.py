import uuid
import json 

class ServoCommand:
    def __init__(self, h_offset: int = 0, v_offset: int = 0, msg_id: int | None = None):
        self.msg_id: int = msg_id if msg_id is not None else (int(uuid.uuid4()) & 0xFFFF)  # 16-bit ID
        self.h_offset = h_offset
        self.v_offset = v_offset

    def to_json(self) -> str:
        return json.dumps({
            "msg_id": self.msg_id,
            "h_offset": self.h_offset,
            "v_offset": self.v_offset
        })

    @classmethod
    def from_json(cls, data: str) -> 'ServoCommand':
        obj = json.loads(data)
        return cls(msg_id=obj['msg_id'], h_offset=obj['h_offset'], v_offset=obj['v_offset'])
    
class AckMessage:
    def __init__(self, msg_id: int):
        self.msg_id = msg_id

    def to_json(self) -> str:
        return json.dumps({
            "msg_id": self.msg_id
        })

    @classmethod
    def from_json(cls, data: str) -> 'AckMessage':
        obj = json.loads(data)
        return cls(msg_id=obj['msg_id'])


class TaskFinishedMessage:
    def __init__(self, msg_id: int):
        self.msg_id = msg_id

    def to_json(self) -> str:
        return json.dumps({
            "msg_id": self.msg_id
        })

    @classmethod
    def from_json(cls, data: str) -> 'TaskFinishedMessage':
        obj = json.loads(data)
        return cls(msg_id=obj['msg_id'])