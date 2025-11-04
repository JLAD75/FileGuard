# 🚀 FileGuard Quick Start Guide

Get FileGuard up and running in **less than 5 minutes**!

## Prerequisites

Before you begin, make sure you have:

- ✅ **Docker** installed (version 24+)
- ✅ **Docker Compose** installed (version 2.0+)
- ✅ **Git** installed
- ✅ At least **4GB RAM** available
- ✅ At least **10GB disk space** available

### Check Prerequisites

```bash
# Check Docker
docker --version
# Should show: Docker version 24.x.x or higher

# Check Docker Compose
docker-compose --version
# Should show: Docker Compose version 2.x.x or higher

# Check Git
git --version
# Should show: git version 2.x.x or higher
```

---

## Step 1: Clone the Repository

```bash
# Clone FileGuard
git clone https://github.com/JLAD75/FileGuard.git

# Navigate into the directory
cd FileGuard
```

---

## Step 2: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Generate a secure secret key
openssl rand -hex 32

# Edit .env and set your SECRET_KEY
# (Use nano, vim, or your favorite editor)
nano .env
```

**Minimum required changes in `.env`:**

```bash
# Change this!
SECRET_KEY=paste-your-generated-key-here

# Optional: Change these if defaults don't work
POSTGRES_PASSWORD=your-secure-password
```

> **💡 Tip:** You can use the defaults for development. Just make sure to change `SECRET_KEY`!

---

## Step 3: Start FileGuard

### Option A: Using Make (Recommended)

```bash
# One command setup and start
make quickstart
```

This will:
- Pull Docker images
- Start all services
- Run database migrations
- Show you the URLs to access

### Option B: Using Docker Compose Directly

```bash
# Start all services
docker-compose up -d

# Wait for services to be healthy (30-60 seconds)
docker-compose ps

# Run database migrations
docker-compose exec backend alembic upgrade head
```

---

## Step 4: Verify Services

Check that all services are running:

```bash
# Check service status
docker-compose ps

# Or use Make
make ps
```

You should see:
- ✅ fileguard-frontend (healthy)
- ✅ fileguard-backend (healthy)
- ✅ fileguard-postgres (healthy)
- ✅ fileguard-redis (healthy)
- ✅ fileguard-minio (healthy)
- ✅ fileguard-clamav (healthy) *(may take a few minutes)*
- ✅ fileguard-celery-worker (running)

### Check Health

```bash
# Check backend health
curl http://localhost:8000/health

# Or use Make
make health
```

---

## Step 5: Access FileGuard

Open your browser and navigate to:

### 🌐 **Frontend Application**
```
http://localhost:3000
```

### 📡 **Backend API**
```
http://localhost:8000
```

### 📚 **API Documentation**
```
http://localhost:8000/docs
```

### 💾 **MinIO Console** (Object Storage)
```
http://localhost:9001
Username: minioadmin
Password: minioadmin
```

---

## Step 6: Create Your First Account

1. Go to **http://localhost:3000**
2. Click **"Register"** or go to the registration form
3. Enter your **email** and **password**
   - Password must be at least 12 characters
   - Include uppercase, lowercase, numbers, and special characters
4. Click **"Sign Up"**
5. You'll be automatically logged in!

---

## Step 7: Upload Your First File

1. After logging in, you'll see the dashboard
2. **Drag and drop** a file onto the upload area
   - Or click the upload button to select a file
3. Watch the upload progress
4. File is automatically **encrypted** before upload
5. **ClamAV** scans for viruses in the background
6. You'll get a notification when the scan completes
7. File appears in your file list!

---

## 🎉 Congratulations!

You're now running FileGuard! Here's what you can do next:

### Explore Features

- 📁 **Upload more files** - Try different file types
- 📂 **Create folders** - Organize your files (coming soon)
- 🏷️ **Add tags** - Categorize your files (coming soon)
- 👥 **Share files** - Share with other users (coming soon)
- 🔍 **Search** - Find files quickly
- 📊 **View analytics** - See your storage usage

### Customize Your Setup

```bash
# Stop services
make stop

# Edit configuration
nano .env

# Restart services
make start
```

### View Logs

```bash
# View all logs
make logs

# View specific service logs
make logs-backend
make logs-frontend
make logs-celery
```

---

## Common Commands

Here are some helpful commands using the **Makefile**:

```bash
# Start services
make start

# Stop services
make stop

# Restart services
make restart

# View logs
make logs

# Run tests
make test

# Database migrations
make migrate

# Open backend shell
make shell

# Check service health
make health

# See all available commands
make help
```

---

## Troubleshooting

### Services Won't Start

```bash
# Check Docker is running
docker ps

# Check logs for errors
docker-compose logs

# Try rebuilding
make clean
make start
```

### Port Already in Use

If ports 3000, 8000, 5432, etc. are already in use:

1. Edit `docker-compose.yml`
2. Change the port mappings:
   ```yaml
   ports:
     - "3001:3000"  # Frontend on 3001 instead of 3000
   ```
3. Restart services

### ClamAV Takes Too Long

ClamAV needs to download virus definitions on first start (can take 5-10 minutes):

```bash
# Check ClamAV logs
docker-compose logs -f clamav

# Wait for: "Self checking every 600 seconds"
```

Alternatively, disable ClamAV for testing:

```bash
# In .env file
CLAMAV_ENABLED=false

# Restart
make restart
```

### Database Issues

```bash
# Reset database (WARNING: deletes all data)
make db-reset

# Or manually
docker-compose down -v postgres
docker-compose up -d postgres
make migrate
```

### Frontend Build Errors

```bash
# Rebuild frontend
cd frontend
rm -rf .next node_modules
npm install
npm run build
```

---

## Security Checklist

Before using in production:

- [ ] Change `SECRET_KEY` to a secure random value
- [ ] Change database passwords
- [ ] Enable HTTPS/TLS
- [ ] Update `CORS_ORIGINS` in `.env`
- [ ] Review firewall rules
- [ ] Enable 2FA for admin accounts
- [ ] Setup regular backups
- [ ] Configure email notifications
- [ ] Review rate limits

See [README.md](README.md#security-checklist) for full checklist.

---

## Next Steps

### Learn More

- 📖 [Full Documentation](README.md)
- 🏗️ [Architecture Guide](ARCHITECTURE.md)
- 🤝 [Contributing Guide](CONTRIBUTING.md)
- 🔒 [Security Best Practices](README.md#security)

### Join the Community

- 💬 [Discord Community](https://discord.gg/fileguard)
- 🐛 [Report Issues](https://github.com/JLAD75/FileGuard/issues)
- ⭐ [Star on GitHub](https://github.com/JLAD75/FileGuard)

### Advanced Topics

- [Production Deployment](README.md#deployment)
- [Kubernetes Setup](docs/deployment/kubernetes.md)
- [AWS Deployment](docs/deployment/aws.md)
- [Performance Tuning](docs/performance.md)
- [API Integration](README.md#api-documentation)

---

## Need Help?

Can't get it working? We're here to help!

1. **Check the logs** - Most issues show up in logs
2. **Search issues** - Someone may have had the same problem
3. **Ask on Discord** - Community is very helpful
4. **Create an issue** - We'll help you debug

---

## Summary

That's it! You've successfully:

- ✅ Installed FileGuard
- ✅ Started all services
- ✅ Created an account
- ✅ Uploaded your first file
- ✅ Explored the interface

**Welcome to FileGuard! 🎉**

---

## Quick Reference Card

```bash
# Essential Commands
make quickstart    # Initial setup and start
make start         # Start services
make stop          # Stop services
make logs          # View logs
make health        # Check health
make help          # All commands

# URLs
Frontend:   http://localhost:3000
Backend:    http://localhost:8000
API Docs:   http://localhost:8000/docs
MinIO:      http://localhost:9001

# Troubleshooting
docker-compose ps        # Check service status
docker-compose logs      # View all logs
make clean && make start # Fresh restart
```

---

**Happy File Managing! 🚀**
