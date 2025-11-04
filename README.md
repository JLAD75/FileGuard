# 🛡️ FileGuard

<div align="center">

![FileGuard Logo](https://via.placeholder.com/200x200?text=FileGuard)

**Enterprise-Grade Secure File Management Platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node 20+](https://img.shields.io/badge/node-20+-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-teal.svg)](https://fastapi.tiangolo.com/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16-black.svg)](https://nextjs.org/)
[![CI/CD](https://github.com/JLAD75/FileGuard/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/JLAD75/FileGuard/actions)
[![codecov](https://codecov.io/gh/JLAD75/FileGuard/branch/main/graph/badge.svg)](https://codecov.io/gh/JLAD75/FileGuard)

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing) • [License](#-license)

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Development](#-development)
- [Deployment](#-deployment)
- [API Documentation](#-api-documentation)
- [Security](#-security)
- [Contributing](#-contributing)
- [License](#-license)
- [Support](#-support)

---

## 🎯 Overview

**FileGuard** is a modern, enterprise-grade file management platform built with security and privacy as top priorities. It provides end-to-end encryption, comprehensive audit logging, antivirus scanning, and advanced collaboration features.

Perfect for:
- 🏢 **Enterprises** requiring secure file storage with compliance
- 🏥 **Healthcare** organizations handling sensitive patient data
- 🏛️ **Government** agencies needing audit trails
- 🎓 **Educational** institutions managing documents
- 💼 **Businesses** wanting self-hosted file storage

### Why FileGuard?

- **🔒 End-to-End Encryption**: AES-256-GCM encryption with per-file DEKs
- **🦠 Antivirus Scanning**: Automatic ClamAV scanning of all uploads
- **📊 Version Control**: Full file versioning with rollback capability
- **👥 Collaboration**: Share files with granular permissions
- **📈 Analytics**: Comprehensive usage analytics and dashboards
- **🐳 Easy Deployment**: Docker-based with one-command setup
- **🔌 S3 Compatible**: Works with AWS S3, MinIO, or local storage
- **🚀 Modern Stack**: FastAPI + Next.js + PostgreSQL + Redis

---

## ✨ Features

### 🔐 Security & Privacy

- **End-to-End Encryption**: Client-side encryption with Web Crypto API
- **Zero-Knowledge Architecture**: Server never sees unencrypted data
- **Two-Factor Authentication (2FA)**: TOTP-based authentication
- **Antivirus Scanning**: Real-time ClamAV integration via Celery
- **Audit Logging**: Comprehensive activity tracking
- **Rate Limiting**: Protection against abuse
- **API Keys**: Secure programmatic access with scopes

### 📁 File Management

- **Chunked Upload**: Resume large file uploads (500MB+)
- **File Versioning**: Automatic version history with rollback
- **Folder Organization**: Hierarchical folder structure
- **Tags & Metadata**: Custom tags for organization
- **Full-Text Search**: Fast search across file names and metadata
- **Bulk Operations**: Multi-file actions (delete, move, share)
- **File Comments**: Collaborate with inline comments

### 🤝 Sharing & Collaboration

- **Granular Permissions**: View, download, edit, admin levels
- **Share Links**: Password-protected public links
- **Expiring Shares**: Time-limited access
- **Access Analytics**: Track who accessed files
- **Notifications**: Real-time WebSocket notifications
- **Team Workspaces**: Shared folders for teams

### 📊 Analytics & Monitoring

- **Usage Dashboard**: Visual analytics with charts
- **Storage Quotas**: Per-user storage limits
- **Access Logs**: Detailed file access history
- **Activity Feed**: Real-time activity stream
- **Export Reports**: CSV/PDF export of analytics
- **Prometheus Metrics**: Integration for monitoring

### 🎨 Modern UI/UX

- **Dark Mode**: Beautiful dark/light theme switching
- **Responsive Design**: Works on mobile, tablet, desktop
- **Drag & Drop**: Intuitive file upload
- **Progressive Web App (PWA)**: Install as native app
- **Animations**: Smooth transitions and interactions
- **Accessibility**: WCAG 2.1 compliant

---

## 🏗️ Architecture

FileGuard follows a modern microservices architecture:

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│   Next.js       │────▶│   FastAPI    │────▶│  PostgreSQL │
│   Frontend      │     │   Backend    │     │  Database   │
└─────────────────┘     └──────────────┘     └─────────────┘
                              │
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
              ┌──────────┐ ┌──────┐ ┌────────┐
              │  Redis   │ │ MinIO│ │ ClamAV │
              │  Cache   │ │  S3  │ │  AV    │
              └──────────┘ └──────┘ └────────┘
                    │
                    ▼
              ┌──────────┐
              │  Celery  │
              │  Workers │
              └──────────┘
```

### Components

- **Frontend**: Next.js 16 with React 19, TypeScript, Mantine UI
- **Backend**: FastAPI with async/await, SQLAlchemy ORM
- **Database**: PostgreSQL 16 with pgvector for search
- **Cache**: Redis for sessions, rate limiting, Celery broker
- **Storage**: MinIO (S3-compatible) or AWS S3
- **Task Queue**: Celery with Redis broker
- **Antivirus**: ClamAV for malware scanning
- **Monitoring**: Prometheus metrics, Sentry error tracking

---

## 🛠️ Tech Stack

### Backend

| Technology | Purpose | Version |
|------------|---------|---------|
| **Python** | Language | 3.11+ |
| **FastAPI** | Web Framework | 0.115+ |
| **SQLAlchemy** | ORM | 2.0+ |
| **Alembic** | Migrations | 1.14+ |
| **Celery** | Task Queue | 5.4+ |
| **Pydantic** | Validation | 2.10+ |
| **JWT** | Authentication | python-jose |
| **Boto3** | S3 Client | 1.35+ |
| **ClamAV** | Antivirus | clamd |

### Frontend

| Technology | Purpose | Version |
|------------|---------|---------|
| **Node.js** | Runtime | 20+ |
| **Next.js** | Framework | 16.0+ |
| **React** | UI Library | 19.0+ |
| **TypeScript** | Language | 5.0+ |
| **Mantine** | UI Components | 8.3+ |
| **Zustand** | State Management | 5.0+ |
| **Axios** | HTTP Client | 1.13+ |

### Infrastructure

| Technology | Purpose | Version |
|------------|---------|---------|
| **Docker** | Containerization | 24+ |
| **Docker Compose** | Orchestration | 2.0+ |
| **PostgreSQL** | Database | 16+ |
| **Redis** | Cache/Broker | 7+ |
| **MinIO** | Object Storage | Latest |
| **Nginx** | Reverse Proxy | 1.25+ (prod) |

---

## 🚀 Quick Start

Get FileGuard running in under 5 minutes!

### Prerequisites

- **Docker** & **Docker Compose** installed
- **Git** for cloning the repository
- **4GB RAM** minimum (8GB recommended)
- **10GB disk space** minimum

### One-Command Setup

```bash
# Clone the repository
git clone https://github.com/JLAD75/FileGuard.git
cd FileGuard

# Copy environment file
cp .env.example .env

# Generate a secure secret key
openssl rand -hex 32 >> .env  # Add to SECRET_KEY in .env

# Start all services
docker-compose up -d

# Wait for services to be healthy (30-60 seconds)
docker-compose ps

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# MinIO Console: http://localhost:9001
```

That's it! 🎉 FileGuard is now running.

### First Steps

1. **Create an account** at http://localhost:3000
2. **Upload your first file** using the drag & drop interface
3. **Share a file** with permissions
4. **Explore the dashboard** for analytics

---

## 💻 Installation

### Option 1: Docker (Recommended)

See [Quick Start](#-quick-start) above.

### Option 2: Manual Installation

<details>
<summary>Click to expand manual installation steps</summary>

#### Backend Setup

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup PostgreSQL database
createdb fileguard_db

# Copy environment file
cp ../.env.example ../.env
# Edit .env with your configuration

# Run migrations
alembic upgrade head

# Start backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local
# Edit .env.local with your API URL

# Start development server
npm run dev
```

#### Celery Worker Setup

```bash
cd backend

# Start Celery worker
celery -A celery_app worker --loglevel=info

# In another terminal, start Celery beat (scheduler)
celery -A celery_app beat --loglevel=info
```

</details>

---

## ⚙️ Configuration

FileGuard uses environment variables for configuration. See `.env.example` for all options.

### Essential Configuration

```bash
# Application
APP_NAME=FileGuard
APP_ENV=production  # development, staging, production
SECRET_KEY=your-super-secret-key-change-this

# Database
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=fileguard
POSTGRES_PASSWORD=secure-password
POSTGRES_DB=fileguard_db

# Storage Backend (choose one)
STORAGE_BACKEND=minio  # Options: minio, s3, local

# MinIO Configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# ClamAV Antivirus
CLAMAV_ENABLED=true
CLAMAV_HOST=localhost
CLAMAV_PORT=3310

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Advanced Configuration

<details>
<summary>Click to see all configuration options</summary>

```bash
# Security
MIN_PASSWORD_LENGTH=12
REQUIRE_SPECIAL_CHARS=true
RATE_LIMIT_PER_MINUTE=60

# File Upload
MAX_FILE_SIZE_MB=500
MAX_CHUNK_SIZE_MB=10
ALLOWED_EXTENSIONS=*  # Or comma-separated: pdf,docx,jpg

# Email (optional)
SMTP_ENABLED=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Monitoring (optional)
SENTRY_ENABLED=false
SENTRY_DSN=your-sentry-dsn
PROMETHEUS_ENABLED=true

# Feature Flags
FEATURE_FILE_VERSIONING=true
FEATURE_FILE_SHARING=true
FEATURE_TWO_FACTOR_AUTH=true
```

</details>

---

## 👩‍💻 Development

### Project Structure

```
FileGuard/
├── backend/                 # FastAPI backend
│   ├── alembic/            # Database migrations
│   ├── auth/               # Authentication module
│   ├── core/               # Core models & config
│   ├── files/              # File management
│   ├── storage/            # Storage backends
│   ├── tasks/              # Celery tasks
│   ├── main.py             # Application entry
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js app directory
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities & helpers
│   │   └── store/         # Zustand state management
│   ├── public/            # Static assets
│   └── package.json       # Node dependencies
│
├── docker-compose.yml     # Docker orchestration
├── .env.example           # Environment template
└── README.md              # This file
```

### Development Workflow

```bash
# Backend development with hot reload
cd backend
uvicorn main:app --reload

# Frontend development with hot reload
cd frontend
npm run dev

# Run tests
cd backend && pytest
cd frontend && npm test

# Linting
cd backend && flake8 .
cd frontend && npm run lint

# Type checking
cd backend && mypy .
cd frontend && npx tsc --noEmit
```

### Database Migrations

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

### Running Tests

```bash
# Backend tests with coverage
cd backend
pytest --cov=. --cov-report=html
# View coverage: open htmlcov/index.html

# Frontend tests
cd frontend
npm test -- --coverage

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

---

## 🚢 Deployment

### Production Deployment

<details>
<summary>Docker Compose Production</summary>

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# Or with environment override
APP_ENV=production docker-compose up -d
```

</details>

<details>
<summary>Kubernetes Deployment</summary>

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n fileguard
```

See `docs/deployment/kubernetes.md` for detailed guide.

</details>

<details>
<summary>AWS Deployment</summary>

Deploy to AWS ECS/EKS with S3 storage:

1. Create S3 bucket for file storage
2. Setup RDS PostgreSQL instance
3. Deploy containers to ECS/EKS
4. Configure ALB for load balancing

See `docs/deployment/aws.md` for step-by-step guide.

</details>

### Security Checklist

Before deploying to production:

- [ ] Change `SECRET_KEY` to a secure random value
- [ ] Use strong database passwords
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Enable backup strategy
- [ ] Setup monitoring and alerts
- [ ] Review CORS origins
- [ ] Enable rate limiting
- [ ] Configure email notifications
- [ ] Setup log rotation

---

## 📚 API Documentation

### Interactive API Docs

When the backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Quick API Reference

#### Authentication

```bash
# Register new user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123!"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123!"}'
```

#### File Operations

```bash
# Initialize file upload
curl -X POST http://localhost:8000/files/upload/init \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "document.pdf",
    "size_bytes": 1024000,
    "mime_type": "application/pdf"
  }'

# List files
curl -X GET http://localhost:8000/files/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Download file
curl -X GET http://localhost:8000/files/download/FILE_ID \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output downloaded_file.pdf
```

See full API documentation at `/docs`.

---

## 🔒 Security

### Security Features

- **🔐 Encryption**: AES-256-GCM end-to-end encryption
- **🛡️ Authentication**: JWT with configurable expiration
- **🔑 2FA**: TOTP-based two-factor authentication
- **🦠 Antivirus**: Automatic ClamAV scanning
- **📝 Audit Logs**: Comprehensive activity logging
- **⏱️ Rate Limiting**: Slowapi integration
- **🚫 Input Validation**: Pydantic schemas
- **🔒 CORS**: Configurable origins
- **🛡️ CSRF Protection**: Token-based protection

### Reporting Security Issues

If you discover a security vulnerability, please email:

**security@fileguard.example.com**

Please do NOT create public GitHub issues for security vulnerabilities.

### Security Best Practices

1. **Regular Updates**: Keep dependencies updated
2. **Strong Passwords**: Enforce password policy
3. **Enable 2FA**: For all admin accounts
4. **HTTPS Only**: Use TLS in production
5. **Backup Strategy**: Regular automated backups
6. **Monitor Logs**: Setup alerts for suspicious activity
7. **Access Control**: Principle of least privilege
8. **Audit Reviews**: Regular security audits

---

## 🤝 Contributing

We love contributions! FileGuard is open source and community-driven.

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- Write **tests** for new features
- Follow **PEP 8** (Python) and **ESLint** (TypeScript) style guides
- Update **documentation** for user-facing changes
- Add **type hints** to all Python functions
- Write **clear commit messages**

### Code Review Process

1. All PRs require approval from at least one maintainer
2. CI/CD tests must pass
3. Code coverage should not decrease
4. Documentation must be updated

### Areas to Contribute

- 🐛 Bug fixes
- ✨ New features
- 📝 Documentation improvements
- 🌐 Translations/i18n
- 🎨 UI/UX enhancements
- ⚡ Performance optimizations
- 🧪 Test coverage

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📄 License

FileGuard is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2024 FileGuard Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

See [LICENSE](LICENSE) for full text.

---

## 💬 Support

### Get Help

- 📖 **Documentation**: [docs.fileguard.example.com](https://docs.fileguard.example.com)
- 💬 **Discord Community**: [Join our Discord](https://discord.gg/fileguard)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/JLAD75/FileGuard/issues)
- ✨ **Feature Requests**: [GitHub Discussions](https://github.com/JLAD75/FileGuard/discussions)
- 📧 **Email**: support@fileguard.example.com

### FAQ

<details>
<summary><strong>Can I use this in production?</strong></summary>

Yes! FileGuard is production-ready. Many organizations use it in production. Make sure to follow the [Security Checklist](#security-checklist).
</details>

<details>
<summary><strong>What's the maximum file size?</strong></summary>

Default is 500MB, configurable via `MAX_FILE_SIZE_MB`. The chunked upload system can handle files of any size with proper storage backend.
</details>

<details>
<summary><strong>Is it truly end-to-end encrypted?</strong></summary>

Yes! Files are encrypted in the browser before upload using Web Crypto API. The server never sees unencrypted content. DEKs are wrapped with user-derived KEKs.
</details>

<details>
<summary><strong>Can I self-host on my own server?</strong></summary>

Absolutely! That's the point. FileGuard is designed for self-hosting with Docker. Works on any VPS, dedicated server, or on-premises infrastructure.
</details>

<details>
<summary><strong>What storage backends are supported?</strong></summary>

- **MinIO** (recommended, S3-compatible)
- **AWS S3**
- **Local filesystem**

More backends (Google Cloud Storage, Azure Blob) coming soon!
</details>

---

## 🙏 Acknowledgments

FileGuard is built with amazing open source technologies:

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Next.js](https://nextjs.org/) - React framework
- [PostgreSQL](https://www.postgresql.org/) - Database
- [Redis](https://redis.io/) - Cache and message broker
- [MinIO](https://min.io/) - S3-compatible storage
- [ClamAV](https://www.clamav.net/) - Antivirus engine
- [Mantine](https://mantine.dev/) - React components
- [Celery](https://docs.celeryproject.org/) - Task queue

Special thanks to all our [contributors](https://github.com/JLAD75/FileGuard/graphs/contributors)!

---

## 🗺️ Roadmap

### v2.1 (Next Release)

- [ ] Mobile apps (React Native)
- [ ] End-to-end encrypted chat
- [ ] Video preview player
- [ ] Document viewer (PDF, Office)
- [ ] Advanced search with filters
- [ ] Trash/recovery feature

### v2.2 (Future)

- [ ] Blockchain audit trail
- [ ] WOPI protocol support
- [ ] Federation/multi-tenant
- [ ] AI-powered file organization
- [ ] Advanced collaboration tools

See [ROADMAP.md](ROADMAP.md) for detailed plans.

---

## ⭐ Star History

If you find FileGuard useful, please consider giving it a star!

[![Star History Chart](https://api.star-history.com/svg?repos=JLAD75/FileGuard&type=Date)](https://star-history.com/#JLAD75/FileGuard&Date)

---

<div align="center">

**Made with ❤️ by the FileGuard community**

[Website](https://fileguard.example.com) • [Documentation](https://docs.fileguard.example.com) • [Blog](https://blog.fileguard.example.com)

</div>
