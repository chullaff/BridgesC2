import uuid
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Message:
    msg_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    route: List[str] = field(default_factory=list)
    payload: Dict = field(default_factory=dict)

    def to_dict(self):
        return {
            "msg_id": self.msg_id,
            "route": self.route,
            "payload": self.payload,
        }

    @staticmethod
    def from_dict(d: Dict):
        return Message(
            msg_id=d.get("msg_id"),
            route=d.get("route", []),
            payload=d.get("payload", {}),
        )
