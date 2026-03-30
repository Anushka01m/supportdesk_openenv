from typing import Any, Dict

from openenv.core.http_env_client import HTTPEnvClient, StepResult
from openenv.core.env_server.types import State

from models import SupportDeskAction, SupportDeskObservation


class SupportDeskEnv(HTTPEnvClient[SupportDeskAction, SupportDeskObservation]):
    """
    Typed HTTP client. Uses openenv.core.* imports (openenv_core is deprecated).
    """

    # Your inference.py uses .sync(), so provide it for compatibility
    def sync(self):
        return self

    def _step_payload(self, action: SupportDeskAction) -> Dict[str, Any]:
        return action.model_dump()

    def _parse_result(self, payload: Dict[str, Any]) -> StepResult[SupportDeskObservation]:
        obs_dict = payload.get("observation", {})
        obs = SupportDeskObservation(**obs_dict)
        return StepResult(
            observation=obs,
            reward=payload.get("reward", obs.reward),
            done=payload.get("done", obs.done),
        )

    def _parse_state(self, payload: Dict[str, Any]) -> State:
        return State(**payload)