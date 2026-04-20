#!/bin/bash
set -e

cd /portal/vue-session

echo "=== Pulling latest code ==="
git pull

echo "=== Installing Python dependencies ==="
source venv/bin/activate
pip install -r requirements.txt

echo "=== Running migrations ==="
python manage.py migrate

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput

echo "=== Building frontend ==="
cd frontend
npm install
npm run build
cd ..

echo "=== Restarting Gunicorn ==="
sudo systemctl restart tbp-gunicorn

echo "=== Reloading Nginx ==="
sudo systemctl reload nginx

echo "=== Done ==="
