#!/bin/bash
# HealthTrack — First deploy script for Ubuntu 22.04 VPS
# Usage: ssh root@your-server 'bash -s' < deploy.sh

set -e

echo "=== 1. System update ==="
apt-get update && apt-get upgrade -y

echo "=== 2. Install Docker ==="
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
fi

echo "=== 3. Install Docker Compose ==="
if ! command -v docker compose &> /dev/null; then
    apt-get install -y docker-compose-plugin
fi

echo "=== 4. Create app directory ==="
mkdir -p /opt/healthtrack
cd /opt/healthtrack

echo "=== 5. Clone or update repository ==="
if [ -d ".git" ]; then
    git pull
else
    echo "Please upload your project files to /opt/healthtrack"
    echo "You can use: scp -r ./healthtrack/* root@your-server:/opt/healthtrack/"
fi

echo "=== 6. Generate secrets ==="
if grep -q "CHANGE_ME" .env.production 2>/dev/null; then
    POSTGRES_PASS=$(openssl rand -hex 24)
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/CHANGE_ME_STRONG_PASSWORD_HERE/$POSTGRES_PASS/" .env.production
    sed -i "s/CHANGE_ME_RANDOM_64_CHAR_STRING_HERE/$SECRET_KEY/" .env.production
    echo "Generated new secrets in .env.production"
fi

echo "=== 7. Get SSL certificate ==="
# First, start nginx with HTTP only for Let's Encrypt challenge
# Create temporary nginx config without SSL
cat > /tmp/nginx-init.conf << 'INITEOF'
server {
    listen 80;
    server_name zhiviy.com www.zhiviy.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 200 'HealthTrack is setting up...';
        add_header Content-Type text/plain;
    }
}
INITEOF

mkdir -p nginx
cp /tmp/nginx-init.conf nginx/nginx-init.conf

# Start nginx temporarily for certificate
docker run -d --name certbot-nginx \
    -p 80:80 \
    -v $(pwd)/nginx/nginx-init.conf:/etc/nginx/conf.d/default.conf:ro \
    -v healthtrack_certbot_www:/var/www/certbot \
    nginx:alpine

sleep 3

# Get certificate
docker run --rm \
    -v healthtrack_certbot_conf:/etc/letsencrypt \
    -v healthtrack_certbot_www:/var/www/certbot \
    certbot/certbot certonly \
    --webroot --webroot-path=/var/www/certbot \
    --email vladislavmarchenkoo@gmail.com \
    --agree-tos --no-eff-email \
    -d zhiviy.com -d www.zhiviy.com

# Stop temporary nginx
docker stop certbot-nginx && docker rm certbot-nginx

echo "=== 8. Build and start all services ==="
docker compose -f docker-compose.prod.yml up -d --build

echo "=== 9. Run database migrations ==="
sleep 10  # Wait for postgres to be ready
docker exec healthtrack_backend bash -c "cd /app && alembic upgrade head"

echo ""
echo "✅ HealthTrack deployed successfully!"
echo "🌐 https://zhiviy.com"
echo ""
echo "Useful commands:"
echo "  docker compose -f docker-compose.prod.yml logs -f      # View logs"
echo "  docker compose -f docker-compose.prod.yml restart       # Restart all"
echo "  docker compose -f docker-compose.prod.yml down          # Stop all"
echo "  docker exec healthtrack_backend alembic upgrade head    # Run migrations"
