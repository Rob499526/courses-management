docker-compose up -d
lt --port 8080 --subdomain coursemanagement
poetry run uvicorn app.main:app --reload