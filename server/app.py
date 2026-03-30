from openenv.core.env_server import create_app
from models import SupportDeskAction, SupportDeskObservation
from .supportdesk_environment import SupportDeskEnvironment

app = create_app(
    SupportDeskEnvironment,
    SupportDeskAction,
    SupportDeskObservation,
    env_name="supportdesk_env",
)

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()