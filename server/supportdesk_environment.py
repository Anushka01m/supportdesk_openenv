import re
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State
from models import SupportDeskObservation, SupportDeskAction, TaskId
from tasks import TASKS, initial_tickets_for
from graders import grade


RE_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
RE_PHONE = re.compile(r"\b(?:\+?\d{1,3}[- ]?)?(?:\d{3}[- ]?\d{3}[- ]?\d{4})\b")
RE_CC = re.compile(r"\b(?:\d[ -]*?){13,19}\b")


def contains_pii(text: str) -> bool:
    return bool(RE_EMAIL.search(text) or RE_PHONE.search(text) or RE_CC.search(text))


def redact(text: str) -> str:
    text = RE_CC.sub("[REDACTED_CC]", text)
    text = RE_EMAIL.sub("[REDACTED_EMAIL]", text)
    text = RE_PHONE.sub("[REDACTED_PHONE]", text)
    return text


class SupportDeskEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS = True

    def __init__(self):
        self._state = State(episode_id="0", step_count=0)
        self._task_id: TaskId | None = None
        self._tickets = {}
        self._actions = []
        self._pii_violation = False
        self._last_score = 0.0
        self._step_limit = 30

    def reset(self):
        self._state = State(episode_id="1", step_count=0)
        self._task_id = None
        self._tickets = {}
        self._actions = []
        self._pii_violation = False
        self._last_score = 0.0

        return SupportDeskObservation(
            message="Reset ok. Use tool=set_task with task_id: easy|medium|hard.",
            task_id=None,
            progress=0.0,
            subscores={},
            reward=0.0,
            done=False,
            info={"tasks": [t.task_id for t in TASKS]},
        )

    def step(self, action: SupportDeskAction):
        self._state.step_count += 1
        self._actions.append(action.model_dump())

        # default shaping: small time penalty
        reward = -0.01
        done = False

        if action.tool == "set_task":
            assert action.task_id is not None
            self._task_id = action.task_id
            self._tickets = {t["ticket_id"]: {**t, "status": "open"} for t in initial_tickets_for(self._task_id)}
            self._last_score = 0.0
            return SupportDeskObservation(
                message=f"Task set to {self._task_id}. Tickets loaded.",
                task_id=self._task_id,
                progress=0.0,
                subscores={},
                reward=0.0,
                done=False,
                info={"tickets": list(self._tickets.keys())},
            )

        if self._task_id is None:
            return SupportDeskObservation(
                message="Task not set. Use set_task first.",
                task_id=None,
                progress=0.0,
                subscores={},
                reward=-0.1,
                done=False,
                info={},
            )

        tid = action.ticket_id

        # Apply actions
        if action.tool == "classify" and tid in self._tickets:
            self._tickets[tid]["category"] = action.category
            self._tickets[tid]["priority"] = action.priority

        elif action.tool == "apply_macro" and tid in self._tickets:
            self._tickets[tid]["last_macro"] = action.macro_id

        elif action.tool == "redact_pii" and tid in self._tickets:
            self._tickets[tid]["body"] = redact(self._tickets[tid]["body"])
            self._tickets[tid]["redacted"] = True

        elif action.tool == "draft_reply" and tid in self._tickets:
            msg = action.message or ""
            if contains_pii(msg):
                self._pii_violation = True
            self._tickets[tid]["last_reply"] = msg

        elif action.tool == "escalate" and tid in self._tickets:
            self._tickets[tid]["status"] = "escalated"
            self._tickets[tid]["escalated_to"] = action.escalate_to

        elif action.tool == "close" and tid in self._tickets:
            self._tickets[tid]["status"] = "closed"
            self._tickets[tid]["resolution_code"] = action.resolution_code

        # Grade (dense reward = delta score)
        score, subs = grade(self._task_id, {"tickets": self._tickets, "actions": self._actions, "pii_violation": self._pii_violation})
        reward += (score - self._last_score)
        self._last_score = score

        if score >= 1.0:
            done = True
        if self._state.step_count >= self._step_limit:
            done = True

        return SupportDeskObservation(
            message="Step applied.",
            task_id=self._task_id,
            progress=score,
            subscores=subs,
            reward=reward,
            done=done,
            info={"score": score, "step_count": self._state.step_count},
        )

    @property
    def state(self):
        return self._state