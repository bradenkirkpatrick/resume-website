# Deploy to AWS EC2

This guide walks through deploying the Resume Website to an AWS EC2 instance running Ubuntu.

## Prerequisites

1. **An AWS Account** with permissions to create EC2 instances
2. **AWS CLI** installed and configured locally
3. **A domain name** (optional, for production)

---

## Step 1: Launch an EC2 Instance

### Via AWS Console

1. Go to EC2 Dashboard → **Launch Instance**
2. Choose name: `resume-website`
3. **AMI**: Ubuntu 24.04 LTS (or 22.04 LTS)
4. **Instance type**: `t2.micro` (free tier eligible) or `t3.medium` for production
5. **Key pair**: Create or select an existing key pair (`.pem` file)
6. **Network settings**:
   - Allow SSH traffic from: `Your IP` (or `0.0.0.0/0` for any, not recommended)
   - Allow HTTP traffic from the internet: ✅
   - Allow HTTPS traffic from the internet: ✅ (if using a domain)
7. **Storage**: 20 GB gp3 (or more as needed)
8. Click **Launch Instance**

### Via AWS CLI

```bash
# Create security group
aws ec2 create-security-group \
    --group-name resume-website-sg \
    --description "Security group for Resume Website"

# Add SSH access
aws ec2 authorize-security-group-ingress \
    --group-name resume-website-sg \
    --protocol tcp --port 22 --cidr YOUR_IP/32

# Add HTTP access
aws ec2 authorize-security-group-ingress \
    --group-name resume-website-sg \
    --protocol tcp --port 80 --cidr 0.0.0.0/0

# Add HTTPS access
aws ec2 authorize-security-group-ingress \
    --group-name resume-website-sg \
    --protocol tcp --port 443 --cidr 0.0.0.0/0

# Add application port access
aws ec2 authorize-security-group-ingress \
    --group-name resume-website-sg \
    --protocol tcp --port 8000 --cidr 0.0.0.0/0

# Launch instance
aws ec2 run-instances \
    --image-id ami-0e86e20dae9224db8 \
    --instance-type t2.micro \
    --key-name your-key-pair \
    --security-groups resume-website-sg \
    --block-device-mappings 'DeviceName=/dev/sda1,Ebs={VolumeSize=20,VolumeType=gp3}'
```

> **Note**: Replace `YOUR_IP` with your actual IP address and `your-key-pair` with your key pair name.

---

## Step 2: Connect to Your EC2 Instance

```bash
# Make sure your key file has proper permissions
chmod 400 /path/to/your-key-pair.pem

# SSH into the instance
ssh -i /path/to/your-key-pair.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

---

## Step 3: Install Dependencies on EC2

Run these commands on the EC2 instance:

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
node --version  # Verify: v20.x.x
npm --version   # Verify: 10.x.x

# Install Python 3 and pip
sudo apt install -y python3 python3-pip python3-venv
python3 --version  # Verify: 3.12.x

# Install Nginx (reverse proxy)
sudo apt install -y nginx
sudo systemctl enable nginx

# Install pm2 (Node.js process manager)
sudo npm install -g pm2

# Install git
sudo apt install -y git
```

---

## Step 4: Clone and Set Up the Application

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/resume-website.git
cd resume-website

# Set up environment variables
cp .env.example .env
nano .env  # Edit with your configuration

# Install all dependencies
make install

# Build frontend for production
cd frontend && npx vite build && cd ..

# Start the application in production mode
make start-prod
```

---

## Step 5: Configure Nginx as a Reverse Proxy

Create an Nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/resume-website
```

Add the following configuration:

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    # Frontend static files
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable the site and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/resume-website /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

---

## Step 6: Set Up PM2 for Process Management

```bash
# Start the backend with pm2
cd ~/resume-website/backend
source venv/bin/activate
pm2 start uvicorn --name "resume-backend" -- app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Start the frontend with pm2
cd ~/resume-website/frontend
pm2 start npx --name "resume-frontend" -- serve dist -l 3000 --no-clipboard

# Save pm2 process list and set to start on boot
pm2 save
pm2 startup
```

---

## Step 7: Set Up SSL with Let's Encrypt (Optional but Recommended)

```bash
sudo apt install -y certbot python3-certbot-nginx

# Obtain and install SSL certificate
sudo certbot --nginx -d YOUR_DOMAIN

# Test auto-renewal
sudo certbot renew --dry-run
```

---

## Step 8: Google Docs Integration (Optional)

To populate the resume automatically from a Google Doc:

1. **Create a Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project (or select existing)
   - Enable the **Google Docs API**

2. **Create a Service Account**:
   - IAM & Admin → Service Accounts → Create Service Account
   - Name: `resume-website`
   - Role: Basic → Viewer
   - Create a JSON key and download it

3. **Upload the key to EC2**:
   ```bash
   scp -i /path/to/your-key-pair.pem /local/path/to/service-account-key.json \
       ubuntu@YOUR_EC2_PUBLIC_IP:~/resume-website/
   ```

4. **Configure the .env file**:
   ```bash
   cd ~/resume-website
   nano .env
   ```
   Set:
   ```
   GOOGLE_DOCS_ID=your-google-doc-id
   GOOGLE_APPLICATION_CREDENTIALS=/home/ubuntu/resume-website/service-account-key.json
   ```

5. **Share your Google Doc** with the service account email.

---

## Useful Commands

### Application Management

```bash
# Start (with restart prompt if running)
make start-prod
make start-prod ARGS="-f"     # Force restart without prompt

# Stop
make stop-prod

# View logs
pm2 logs resume-backend
pm2 logs resume-frontend
pm2 monit  # Interactive monitoring dashboard

# Check status
pm2 status
```

### System Management

```bash
# Check Nginx status
sudo systemctl status nginx

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Restart services after config changes
sudo systemctl restart nginx
pm2 restart all

# Monitor system resources
htop
df -h
free -h
```

### Updates & Maintenance

```bash
# Pull latest code
cd ~/resume-website
git pull origin main

# Rebuild frontend
cd frontend && npx vite build && cd ..

# Restart services
pm2 restart all

# Full update cycle
git pull && make install && cd frontend && npx vite build && cd .. && pm2 restart all
```

---

## One-Line Deploy Command

Run this from your local machine after the EC2 instance is set up:

```bash
# Deploy latest code to EC2
ssh -i /path/to/your-key-pair.pem ubuntu@YOUR_EC2_PUBLIC_IP \
    "cd ~/resume-website && git pull && make install && \
     cd frontend && npx vite build && cd .. && pm2 restart all"
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't connect to EC2 | Check security group inbound rules |
| Nginx 502 Bad Gateway | Ensure backend is running: `pm2 status` |
| Frontend shows blank page | Check browser console, ensure Vite build succeeded |
| Google Docs API error | Verify service account key path and Doc ID |
| Port already in use | `lsof -i :8000` then `kill -9 <PID>` |
| Permission denied (key) | `chmod 400 /path/to/key.pem` |

---

## Architecture

```
┌─────────┐      ┌──────────┐      ┌──────────┐
│ Browser │─────▶│  Nginx   │─────▶│ Frontend │
│  :443   │      │  :80/443 │      │  :3000   │
└─────────┘      └──────────┘      └──────────┘
                        │
                        ▼
                  ┌──────────┐      ┌──────────────┐
                  │  Backend │─────▶│  Google Docs  │
                  │  :8000   │      │  API (opt.)   │
                  └──────────┘      └──────────────┘
```

The static frontend files are served via `serve` on port 3000. API requests are proxied through Nginx to the FastAPI backend on port 8000.
