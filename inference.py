import json
import os
import requests

ENV_BASE_URL = os.environ.get("ENV_BASE_URL", "http://localhost:8000")
MAX_STEPS = 15


def post_json(url: str, payload: dict):
    r = requests.post(url, json=payload, timeout=10)
    r.raise_for_status()
    return r.json()


def main():
    print(">>> inference started")

    scores = {}

    for task_id in ["easy", "medium", "hard"]:
        # reset
        post_json(f"{ENV_BASE_URL}/reset", {})

        # set task (IMPORTANT: wrap in "action")
        step_out = post_json(
            f"{ENV_BASE_URL}/step",
            {"action": {"tool": "set_task", "task_id": task_id}},
        )

        for _ in range(MAX_STEPS):
            if step_out.get("done", False):
                break

            step_out = post_json(
                f"{ENV_BASE_URL}/step",
                {"action": {"tool": "noop"}},
            )

        obs = step_out.get("observation", {})
        info = obs.get("info", {}) or {}
        score = float(info.get("score", obs.get("progress", 0.0)))
        scores[task_id] = score

    result = {
        "scores": scores,
        "average": sum(scores.values()) / 3.0,
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()