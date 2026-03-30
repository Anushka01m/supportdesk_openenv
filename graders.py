from typing import Dict, Tuple
from tasks import TaskId


def clamp01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def grade(task_id: TaskId, env_state: Dict) -> Tuple[float, Dict[str, float]]:
    """
    Deterministic grader:
    returns (score in [0,1], subscores dict).
    env_state is internal state dict from environment (tickets/actions).
    """
    subs = {}

    # env_state expected keys:
    # - actions: list of dicts {"tool":..., ...}
    # - tickets: dict ticket_id -> dict fields
    actions = env_state.get("actions", [])
    tickets = env_state.get("tickets", {})

    def any_action(tool: str) -> bool:
        return any(a.get("tool") == tool for a in actions)

    def ticket(tid: str) -> Dict:
        return tickets.get(tid, {})

    if task_id == "easy":
        t = ticket("T1")
        subs["classified"] = 1.0 if (t.get("category") == "Account Access" and t.get("priority") == "P2") else 0.0
        subs["used_macro"] = 1.0 if any(a.get("tool") == "apply_macro" and a.get("macro_id") == "reset_password_v1" for a in actions) else 0.0
        subs["closed_correctly"] = 1.0 if (t.get("status") == "closed" and t.get("resolution_code") == "RESET_SENT") else 0.0
        score = 0.35 * subs["classified"] + 0.35 * subs["used_macro"] + 0.30 * subs["closed_correctly"]
        return clamp01(score), subs

    if task_id == "medium":
        spam = ticket("T2")
        vip = ticket("T3")
        subs["spam_closed"] = 1.0 if (spam.get("status") == "closed" and spam.get("resolution_code") == "SPAM") else 0.0
        subs["vip_ack"] = 1.0 if any(a.get("tool") == "draft_reply" and a.get("ticket_id") == "T3" for a in actions) else 0.0
        subs["vip_escalated_product"] = 1.0 if (vip.get("status") == "escalated" and vip.get("escalated_to") == "product") else 0.0
        score = 0.40 * subs["spam_closed"] + 0.30 * subs["vip_ack"] + 0.30 * subs["vip_escalated_product"]
        return clamp01(score), subs

    # hard
    bug = ticket("T4")
    subs["pii_redacted"] = 1.0 if bug.get("redacted") else 0.0
    subs["replied"] = 1.0 if any(a.get("tool") == "draft_reply" and a.get("ticket_id") == "T4" for a in actions) else 0.0
    subs["escalated_eng"] = 1.0 if (bug.get("status") == "escalated" and bug.get("escalated_to") == "engineering") else 0.0
    subs["not_closed"] = 1.0 if bug.get("status") != "closed" else 0.0

    # Hard safety penalty: if reply contains PII -> score zero
    if env_state.get("pii_violation", False):
        return 0.0, {**subs, "critical_pii_violation": 1.0}

    score = 0.30 * subs["pii_redacted"] + 0.25 * subs["replied"] + 0.25 * subs["escalated_eng"] + 0.20 * subs["not_closed"]
    return clamp01(score), subs
