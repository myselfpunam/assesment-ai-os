#!/bin/bash
# Run this ONCE to bootstrap the project locally (without Docker)

set -e

echo "=== Assessment AI OS — Local Setup ==="

# 1. Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# 2. Activate
source venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

# 4. Run migrations
cd assessment_ai
python ../manage.py migrate
echo "✓ Database migrated"

# 5. Seed roles
python ../manage.py seed_roles
echo "✓ Roles seeded"

# 6. Create super admin
python ../manage.py create_super_admin
echo "✓ Super Admin created"

echo ""
echo "=== Setup Complete ==="
echo "Run: python manage.py runserver"
echo "Login: admin@assessmentai.com / Admin@123456"
