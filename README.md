# SupportDesk OpenEnv

An OpenEnv-based support desk environment with Docker deployment and a working inference script.

## How to run locally

```bash
docker build -t supportdesk-openenv .
docker run -p 8000:8000 supportdesk-openenv
python inference.py
