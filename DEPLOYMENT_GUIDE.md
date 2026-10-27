# Deployment Guide

## 🎯 Overview

This guide covers deploying the AI Smart Safety Monitoring System in various environments:
- Local development
- Docker containerization
- Production deployment
- Cloud deployment (AWS, Azure, etc.)

## 🏠 Local Development Setup

### Windows (PowerShell)

1. **Clone/Navigate to project**
```powershell
cd d:\major project
```

2. **Create virtual environment**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Install dependencies**
```powershell
pip install -r requirements.txt
```

4. **Configure environment**
```powershell
cp .env.template .env
# Edit .env with your settings
```

5. **Run application**
```powershell
python main.py
```

Access at: `http://localhost:5000`

### Linux/macOS (Bash)

```bash
# Navigate to project
cd /path/to/major\ project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env with settings

# Run application
python main.py
```

## 🐳 Docker Deployment

### Prerequisites
- Docker 20.10+
- Docker Compose 1.29+

### Development with Docker

1. **Build development image**
```bash
docker build -t safety-monitoring:dev --target development .
```

2. **Run development container**
```bash
docker-compose up -d
```

3. **Access application**
```bash
# Access main app
http://localhost:5000

# View logs
docker-compose logs -f app

# Enter container shell
docker exec -it ai-safety-dev bash
```

### Production Build

1. **Build production image**
```bash
docker build -t safety-monitoring:latest --target production .
```

2. **Tag for registry** (if using Docker Hub or private registry)
```bash
docker tag safety-monitoring:latest myregistry.azurecr.io/safety-monitoring:latest
```

3. **Push to registry**
```bash
docker push myregistry.azurecr.io/safety-monitoring:latest
```

### Docker Deployment with Compose

1. **Create .env file for production**
```bash
cp .env.template .env.production
# Edit with production values
```

2. **Start all services**
```bash
docker-compose --env-file .env.production up -d
```

3. **Verify services running**
```bash
docker-compose ps
```

4. **View logs**
```bash
docker-compose logs -f app
docker-compose logs -f db
docker-compose logs -f redis
```

5. **Stop services**
```bash
docker-compose down
```

## 🚀 Production Deployment (Linux Server)

### Server Requirements
- Ubuntu 20.04+ or CentOS 8+
- Python 3.12
- PostgreSQL 13+
- Redis 6+
- 8GB RAM minimum
- 50GB disk space
- SSL certificate

### 1. Server Setup

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y \
    python3.12 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    supervisor \
    git \
    curl \
    wget

# Create application user
sudo useradd -m -s /bin/bash safety-app
sudo usermod -aG sudo safety-app
```

### 2. Application Setup

```bash
# Switch to application user
sudo su - safety-app

# Clone repository (or copy your code)
git clone <repository> /home/safety-app/app
cd /home/safety-app/app

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy configuration
cp .env.template .env
# Edit .env with production settings
```

### 3. Database Setup

```bash
# Create PostgreSQL database
sudo -u postgres psql

# In PostgreSQL:
CREATE USER safety_user WITH PASSWORD 'strong-password';
CREATE DATABASE safety_monitoring OWNER safety_user;
GRANT ALL PRIVILEGES ON DATABASE safety_monitoring TO safety_user;
\q
```

### 4. Gunicorn Configuration

Create `/home/safety-app/app/gunicorn_config.py`:
```python
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
```

### 5. Supervisor Configuration

Create `/etc/supervisor/conf.d/safety-monitoring.conf`:
```ini
[program:safety-monitoring]
directory=/home/safety-app/app
command=/home/safety-app/app/venv/bin/gunicorn \
    -c gunicorn_config.py \
    -b 127.0.0.1:8000 \
    'main:create_app()'
user=safety-app
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/safety-monitoring/gunicorn.log
environment=FLASK_ENV="production"
```

Start supervisor:
```bash
sudo systemctl restart supervisor
sudo supervisorctl status
```

### 6. Nginx Configuration

Create `/etc/nginx/sites-available/safety-monitoring`:
```nginx
upstream app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name safety.your-domain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name safety.your-domain.com;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/safety.your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/safety.your-domain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
    
    location /static/ {
        alias /home/safety-app/app/frontend/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location ~ ^/(health|metrics)$ {
        access_log off;
        proxy_pass http://app;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/safety-monitoring /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. SSL Certificate

Using Let's Encrypt (Certbot):
```bash
sudo apt-get install certbot python3-certbot-nginx -y
sudo certbot certonly --nginx -d safety.your-domain.com
```

### 8. Firewall Configuration

```bash
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable
```

### 9. Monitoring & Logging

```bash
# Create log directory
sudo mkdir -p /var/log/safety-monitoring
sudo chown safety-app:safety-app /var/log/safety-monitoring

# Set up log rotation
sudo cat > /etc/logrotate.d/safety-monitoring << EOF
/var/log/safety-monitoring/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 safety-app safety-app
    sharedscripts
    postrotate
        systemctl reload supervisor > /dev/null 2>&1 || true
    endscript
}
EOF
```

### 10. Backup Configuration

Create `/home/safety-app/backup.sh`:
```bash
#!/bin/bash

BACKUP_DIR="/home/safety-app/backups"
DATE=$(date +"%Y%m%d_%H%M%S")

# Backup database
sudo -u postgres pg_dump safety_monitoring | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup application data
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /home/safety-app/app

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

Make executable and add to crontab:
```bash
chmod +x /home/safety-app/backup.sh
crontab -e
# Add: 0 2 * * * /home/safety-app/backup.sh
```

## ☁️ Cloud Deployment

### AWS Deployment

1. **Create EC2 instance**
   - Ubuntu 20.04 AMI
   - t3.medium or better
   - Security group: 80, 443, 22

2. **Use provided server setup steps above**

3. **Configure RDS (PostgreSQL)**
4. **Configure ElastiCache (Redis)**
5. **Use Application Load Balancer**

### Azure Deployment

1. **Create App Service**
   - Python 3.12 runtime
   - App Service Plan (B2 or higher)

2. **Configure PostgreSQL Database**
3. **Configure Azure Cache for Redis**
4. **Deploy via Git or Docker**

### Kubernetes Deployment

1. **Build Docker image**
2. **Create deployment manifests**:
   - `deployment.yaml`
   - `service.yaml`
   - `configmap.yaml`
   - `secret.yaml`

3. **Deploy**:
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl get pods
```

## 🔒 Security Checklist

- [ ] SSL/TLS configured
- [ ] Firewall configured
- [ ] Strong secret keys generated
- [ ] Database password secured
- [ ] Environment variables not in code
- [ ] Regular backups enabled
- [ ] Monitoring configured
- [ ] Log rotation configured
- [ ] Security headers set
- [ ] Rate limiting configured

## 📊 Monitoring Setup

### Health Check
```bash
curl https://safety.your-domain.com/health
```

### Metrics Endpoint
```bash
curl https://safety.your-domain.com/metrics
```

## 🐛 Troubleshooting

### Application won't start
```bash
sudo supervisorctl tail safety-monitoring
```

### Database connection fails
```bash
sudo -u postgres psql -d safety_monitoring -c "SELECT 1;"
```

### Redis connection fails
```bash
redis-cli ping
# Should return: PONG
```

### SSL certificate issues
```bash
sudo certbot renew --dry-run
```

---

For additional help, see [ARCHITECTURE.md](ARCHITECTURE.md) and [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
