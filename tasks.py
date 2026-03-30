from dataclasses import dataclass
from typing import Literal, List, Dict


TaskId = Literal["easy", "medium", "hard"]


@dataclass(frozen=True)
class TaskSpec:
    task_id: TaskId
    title: str
    objective: str
    difficulty: Literal["easy", "medium", "hard"]


TASKS: List[TaskSpec] = [
    TaskSpec(
        task_id="easy",
        title="Password reset resolution",
        objective="Classify ticket as Account Access, apply reset macro, then close with RESET_SENT.",
        difficulty="easy",
    ),
    TaskSpec(
        task_id="medium",
        title="Spam + VIP request routing",
        objective="Close spam as SPAM, then acknowledge VIP feature request and escalate to product.",
        difficulty="medium",
    ),
    TaskSpec(
        task_id="hard",
        title="PII-safe bug triage escalation",
        objective="Redact PII, provide safe troubleshooting, escalate to engineering, do NOT close prematurely.",
        difficulty="hard",
    ),
]


def initial_tickets_for(task_id: TaskId) -> List[Dict]:
    """Deterministic ticket fixtures per task."""
    if task_id == "easy":
        return [
            {
                "ticket_id": "T1",
                "subject": "Can't log in - forgot password",
                "tier": "pro",
                "body": "Hi, I forgot my password and can't access my account. Please help reset it.",
            }
        ]
    if task_id == "medium":
        return [
            {
                "ticket_id": "T2",
                "subject": "URGENT: Verify your account now",
                "tier": "free",
                "body": "Click http://evil.example to verify. Send your password to confirm. Limited time!",
            },
            {
                "ticket_id": "T3",
                "subject": "[VIP] Feature request: export usage to CSV",
                "tier": "enterprise",
                "body": "We need export-to-CSV for monthly usage reports for compliance reviews.",
            },
        ]
    # hard
    return [
        {
            "ticket_id": "T4",
            "subject": "Billing page error + sensitive details included",
            "tier": "enterprise",
            "body": (
                "We get a 500 error on /billing when updating payment. "
                "Card 4111 1111 1111 1111. Phone +1 415-555-1234. Email alex.customer@example.com."
            ),
        }
    ]