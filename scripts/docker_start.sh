#!/bin/bash
# Start with Docker (recommended)

set -e

echo "=== Starting Assessment AI OS with Docker ==="

# Start containers
docker-compose up -d db redis
echo "Waiting for DB and Redis..."
sleep 5

# Run migrations inside web container
docker-compose run --rm web python manage.py migrate
docker-compose run --rm web python manage.py seed_roles
docker-compose run --rm web python manage.py create_super_admin

# Start all services
docker-compose up -d

echo ""
echo "=== All services started ==="
echo "API:       http://localhost:8000"
echo "Admin:     http://localhost:8000/admin"
echo "Login:     admin@assessmentai.com / Admin@123456"
