docker-compose up -d
lt --port 8000 --subdomain coursemanagement
poetry run uvicorn app.main:app --reload