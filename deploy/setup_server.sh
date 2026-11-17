#!/bin/bash
# ==============================================================================
# Automated Server Setup Script for 3D Movie Booking Platform
# Target OS: Ubuntu 22.04 / 24.04 LTS (AWS EC2 / DigitalOcean / Linode / VPS)
# ==============================================================================

set -e

echo ">>> [1/7] Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y python3-pip python3-venv python3-dev nginx git curl libpq-dev

PROJECT_DIR="/home/ubuntu/3d-movie-booking"
if [ ! -d "$PROJECT_DIR" ]; then
    echo ">>> Error: Project directory $PROJECT_DIR does not exist."
    echo ">>> Please clone your repository into $PROJECT_DIR first:"
    echo "    git clone https://github.com/prajwalnp11/3D-MOVIE-BOOKING.git $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

echo ">>> [2/7] Creating Python Virtual Environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ">>> [3/7] Setting up Environment Variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ">>> Generated .env from .env.example. Please update your SECRET_KEY and ALLOWED_HOSTS!"
fi

echo ">>> [4/7] Running database migrations..."
python manage.py migrate

echo ">>> [5/7] Loading Movie & Showtime Catalog..."
if [ -f "movies/fixtures/all_movies_and_shows.json" ]; then
    python manage.py loaddata movies/fixtures/all_movies_and_shows.json
fi

echo ">>> [6/7] Collecting static assets..."
python manage.py collectstatic --noinput

echo ">>> [7/7] Setting up Systemd Service and Nginx..."
sudo cp deploy/cinema.service /etc/systemd/system/cinema.service
sudo systemctl daemon-reload
sudo systemctl enable cinema
sudo systemctl restart cinema

sudo cp deploy/nginx.conf /etc/nginx/sites-available/cinema
sudo ln -sf /etc/nginx/sites-available/cinema /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

echo "=============================================================================="
echo "✔ Deployment complete! Your application is live at http://<your-server-ip>"
echo "  To view logs: journalctl -u cinema -f"
echo "  To install SSL (HTTPS): sudo apt install certbot python3-certbot-nginx && sudo certbot --nginx"
echo "=============================================================================="
