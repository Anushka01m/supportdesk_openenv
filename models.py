from typing import Optional, Literal, Dict, Any
from openenv.core.env_server.types import Action, Observation

TaskId = Literal["easy", "medium", "hard"]

Tool = Literal[
    "set_task",
    "select_ticket",
    "classify",
    "apply_macro",
    "draft_reply",
    "redact_pii",
    "escalate",
    "close",
    "noop",
]

class SupportDeskAction(Action):
    tool: Tool
    task_id: Optional[TaskId] = None

    ticket_id: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None

    macro_id: Optional[str] = None
    message: Optional[str] = None

    escalate_to: Optional[str] = None
    resolution_code: Optional[str] = None

class SupportDeskObservation(Observation):
    message: str
    task_id: Optional[TaskId] = None
    progress: float = 0.0
    subscores: Dict[str, float] = {}
    info: Dict[str, Any] = {}