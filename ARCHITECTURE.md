# FileGuard Architecture

This document provides a comprehensive overview of FileGuard's architecture, design decisions, and implementation details.

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Backend Architecture](#backend-architecture)
- [Frontend Architecture](#frontend-architecture)
- [Data Flow](#data-flow)
- [Security Architecture](#security-architecture)
- [Storage Architecture](#storage-architecture)
- [Scalability](#scalability)
- [Monitoring & Observability](#monitoring--observability)

---

## Overview

FileGuard is designed as a modern, secure, and scalable file management platform. The architecture follows these principles:

* **Security First**: End-to-end encryption, zero-knowledge architecture
* **Scalability**: Horizontal scaling capability for all components
* **Modularity**: Loosely coupled services with clear interfaces
* **Cloud Native**: Container-based, storage-agnostic design
* **Observability**: Comprehensive logging, metrics, and tracing

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  Browser   │  │   Mobile   │  │  Desktop   │            │
│  │    Web     │  │    App     │  │    App     │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────────────────────────────────────────┘
                           │
                    HTTPS / WSS
                           │
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Load Balancer / Reverse Proxy            │  │
│  │                    (Nginx / ALB)                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│       ┌───────────────────┴───────────────────┐             │
│       ▼                                       ▼             │
│  ┌─────────────┐                       ┌─────────────┐     │
│  │   Next.js   │                       │   FastAPI   │     │
│  │   Frontend  │◄─────REST/WS─────────►│   Backend   │     │
│  │  (Port 3000)│                       │  (Port 8000)│     │
│  └─────────────┘                       └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
                                               │
                    ┌──────────────────────────┼──────────────┐
                    ▼                          ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  PostgreSQL  │  │    Redis     │  │    MinIO     │     │
│  │   Database   │  │  Cache/Queue │  │  S3 Storage  │     │
│  │ (Port 5432)  │  │ (Port 6379)  │  │ (Port 9000)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │    ClamAV    │  │    Celery    │                        │
│  │  Antivirus   │  │   Workers    │                        │
│  │ (Port 3310)  │  │              │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### Component Communication

```
Frontend ─────REST API───────► Backend
            ◄────JSON─────────

Frontend ─────WebSocket──────► Backend (Notifications)
            ◄────Events───────

Backend ──────SQL────────────► PostgreSQL
           ◄────Data─────────

Backend ──────Cache──────────► Redis
           ◄────Data─────────

Backend ──────S3 API─────────► MinIO/S3
           ◄────Objects──────

Backend ──────Tasks──────────► Celery (via Redis)
Celery  ──────Scan───────────► ClamAV
           ◄────Result───────
```

---

## Backend Architecture

### FastAPI Application Structure

```
backend/
├── main.py                    # Application entry point
├── core/
│   ├── config.py              # Configuration management
│   ├── database.py            # Database connection
│   ├── models.py              # SQLAlchemy models
│   └── models_extended.py     # Extended models (v2)
├── auth/
│   ├── router.py              # Auth endpoints
│   ├── security.py            # Password hashing, JWT
│   ├── dependencies.py        # Auth dependencies
│   └── schemas.py             # Pydantic schemas
├── files/
│   ├── router.py              # File endpoints
│   ├── schemas.py             # File schemas
│   └── utils.py               # File utilities
├── storage/
│   ├── base.py                # Storage interface
│   ├── factory.py             # Storage backend factory
│   ├── s3_storage.py          # S3 implementation
│   ├── minio_storage.py       # MinIO implementation
│   └── local_storage.py       # Local filesystem
├── tasks/
│   ├── antivirus.py           # Virus scanning tasks
│   ├── notifications.py       # Email tasks
│   └── cleanup.py             # Cleanup tasks
└── celery_app.py              # Celery configuration
```

### Request Lifecycle

1. **Request arrives** at FastAPI application
2. **Middleware** processes request (CORS, rate limiting)
3. **Route** matched to endpoint function
4. **Dependencies** injected (auth, database session)
5. **Validation** performed by Pydantic schemas
6. **Business logic** executed
7. **Response** serialized and returned
8. **Background tasks** scheduled if needed (Celery)

### Database Models

#### Core Models

```python
# User
├── id (UUID)
├── email (String, unique)
├── hashed_password (String)
├── created_at (DateTime)
├── Relationships:
│   ├── files (FileMetadata[])
│   ├── settings (UserSettings)
│   └── audit_logs (AuditLog[])

# FileMetadata
├── id (UUID)
├── owner_id (UUID, FK)
├── size_bytes (BigInteger)
├── mime_type (String)
├── original_filename_encrypted (Text)
├── wrapped_dek (Text)
├── upload_status (String)
├── av_scan_status (String)
├── created_at, updated_at (DateTime)
└── Relationships:
    ├── owner (User)
    ├── versions (FileVersion[])
    ├── shares (FileShare[])
    └── comments (FileComment[])
```

#### Extended Models (v2)

```python
# File Organization
├── Folder (hierarchical structure)
├── Tag (user-defined tags)
└── FileVersion (version history)

# Sharing
├── FileShare (user-to-user sharing)
└── ShareLink (public links)

# Collaboration
├── FileComment (inline comments)
└── Notification (real-time notifications)

# Security
├── UserSettings (2FA, preferences)
└── APIKey (programmatic access)

# Analytics
└── FileAnalytics (access tracking)
```

### API Design

**RESTful Principles:**

```
GET    /api/files/              # List files
POST   /api/files/upload/init   # Initialize upload
POST   /api/files/upload/{id}/chunk   # Upload chunk
POST   /api/files/upload/{id}/complete # Finalize
GET    /api/files/{id}          # Get file metadata
GET    /api/files/download/{id} # Download file
PUT    /api/files/{id}          # Update metadata
DELETE /api/files/{id}          # Delete file
```

**WebSocket Events:**

```
ws://api/ws

Client → Server:
  - ping
  - subscribe:notifications
  - unsubscribe:notifications

Server → Client:
  - notification:file_shared
  - notification:scan_complete
  - notification:comment_added
```

---

## Frontend Architecture

### Next.js Application Structure

```
frontend/
├── src/
│   ├── app/                   # Next.js 13+ App Router
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home/auth page
│   │   ├── dashboard/
│   │   │   └── page.tsx       # Dashboard
│   │   └── api/               # API routes
│   │
│   ├── components/            # React components
│   │   ├── FileUpload.tsx     # Upload component
│   │   ├── FileList.tsx       # File listing
│   │   ├── FileCard.tsx       # Individual file
│   │   └── shared/            # Shared components
│   │
│   ├── lib/                   # Utilities
│   │   ├── api.ts             # API client
│   │   ├── crypto.ts          # Encryption utilities
│   │   └── utils.ts           # Helper functions
│   │
│   ├── store/                 # State management
│   │   ├── auth.ts            # Auth state (Zustand)
│   │   ├── files.ts           # File state
│   │   └── ui.ts              # UI state (theme, etc)
│   │
│   └── types/                 # TypeScript types
│       ├── api.ts             # API types
│       └── models.ts          # Data models
│
└── public/                    # Static assets
```

### State Management

Using **Zustand** for global state:

```typescript
// Auth Store
interface AuthStore {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

// Files Store
interface FilesStore {
  files: FileMetadata[];
  selectedFiles: Set<string>;
  fetchFiles: () => Promise<void>;
  uploadFile: (file: File) => Promise<void>;
  deleteFile: (fileId: string) => Promise<void>;
}

// UI Store
interface UIStore {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  toggleTheme: () => void;
  toggleSidebar: () => void;
}
```

### Component Architecture

**Atomic Design Pattern:**

```
Atoms (smallest components)
├── Button
├── Input
├── Icon
└── Badge

Molecules (combinations of atoms)
├── SearchBar
├── FileCard
└── NotificationItem

Organisms (complete UI sections)
├── FileList
├── FileUpload
├── Sidebar
└── Header

Templates (page layouts)
├── DashboardLayout
└── AuthLayout

Pages (actual routes)
├── HomePage
├── DashboardPage
└── SettingsPage
```

---

## Data Flow

### File Upload Flow

```
1. User selects file in browser
        ↓
2. Frontend encrypts file chunks
   - Generate DEK
   - Encrypt with DEK
   - Wrap DEK with KEK (from password)
        ↓
3. POST /files/upload/init
   ← Returns file_id
        ↓
4. For each chunk:
   POST /files/upload/{file_id}/chunk
   - Sends encrypted chunk
   - Backend stores in MinIO/S3
        ↓
5. POST /files/upload/{file_id}/complete
   - Backend combines chunks
   - Triggers antivirus scan (Celery)
        ↓
6. Celery worker scans file
   - ClamAV checks for viruses
   - Updates av_scan_status
        ↓
7. WebSocket notification
   - "Scan complete" sent to user
        ↓
8. Frontend updates file list
```

### File Download Flow

```
1. User clicks download button
        ↓
2. GET /files/download/{file_id}
   - Backend checks permissions
   - Streams encrypted file from storage
        ↓
3. Frontend receives encrypted chunks
        ↓
4. Frontend decrypts chunks
   - Unwrap DEK with KEK
   - Decrypt chunks with DEK
        ↓
5. Browser downloads decrypted file
        ↓
6. Backend logs download event
   - Updates FileAnalytics
   - Audit log entry
```

### Authentication Flow

```
1. User enters email/password
        ↓
2. POST /auth/login
   - Backend verifies credentials
   - Generates JWT token
        ↓
3. Frontend stores token
   - In Zustand store (memory)
   - Optional: sessionStorage
        ↓
4. All subsequent requests
   - Include "Authorization: Bearer {token}"
        ↓
5. Backend validates token
   - Extracts user_id
   - Checks expiration
        ↓
6. Token expires after 30 minutes
   - Frontend detects 401 response
   - Redirects to login
```

---

## Security Architecture

### Encryption Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Client Side                        │
│                                                      │
│  User Password                                       │
│       │                                              │
│       ▼                                              │
│  PBKDF2 (100k iterations)                           │
│       │                                              │
│       ▼                                              │
│  KEK (Key Encryption Key)                           │
│       │                                              │
│  ┌────┴────────────────┐                            │
│  │                     │                            │
│  ▼                     ▼                            │
│  Generate DEK      Wrap DEK with KEK               │
│  (per file)         (AES-GCM)                      │
│       │                     │                       │
│       ▼                     ▼                       │
│  Encrypt File      Send Wrapped DEK                │
│  with DEK           to Server                       │
│  (AES-256-GCM)             │                        │
│       │                     │                       │
│       └─────────┬───────────┘                       │
│                 │                                    │
└─────────────────┼────────────────────────────────────┘
                  │
                  ▼
          ┌──────────────────┐
          │   Server Side     │
          │                   │
          │  Store:           │
          │  - Encrypted File │
          │  - Wrapped DEK    │
          │                   │
          │  Never sees:      │
          │  - Plaintext File │
          │  - Unwrapped DEK  │
          │  - KEK            │
          └──────────────────┘
```

### Security Layers

1. **Transport Security**: HTTPS/TLS 1.3
2. **Authentication**: JWT with short expiration
3. **Authorization**: Role-based access control
4. **Encryption**: End-to-end AES-256-GCM
5. **Antivirus**: ClamAV scanning all uploads
6. **Rate Limiting**: Per-IP and per-user limits
7. **Audit Logging**: All actions logged
8. **2FA**: Optional TOTP authentication

### Zero-Knowledge Architecture

**Server never has access to:**

* Unencrypted file content
* User's KEK (derived from password)
* Unwrapped DEKs

**Server only stores:**

* Encrypted files
* Wrapped DEKs (encrypted with user's KEK)
* File metadata (size, type, timestamps)

---

## Storage Architecture

### Storage Abstraction

```python
class StorageBackend(ABC):
    @abstractmethod
    async def upload_chunk(file_id, chunk, user_id): ...

    @abstractmethod
    async def finalize_upload(file_id, total_chunks, user_id): ...

    @abstractmethod
    async def download_file(file_id, user_id): ...

    @abstractmethod
    async def delete_file(file_id, user_id): ...
```

### Implementations

```
Local Storage
├── Path: /var/lib/fileguard/storage/
├── Structure: users/{user_id}/files/{file_id}
├── Pros: Simple, no external dependencies
└── Cons: Not scalable, single point of failure

MinIO (Default)
├── Endpoint: minio:9000
├── Bucket: fileguard-files
├── Pros: S3-compatible, self-hosted, scalable
└── Cons: Requires separate service

AWS S3
├── Region: Configurable
├── Bucket: Configurable
├── Pros: Highly available, globally distributed
└── Cons: Vendor lock-in, costs
```

### File Organization in Storage

```
Bucket: fileguard-files
│
├── users/
│   ├── {user_id_1}/
│   │   ├── files/
│   │   │   ├── {file_id_1}        # Final file
│   │   │   └── {file_id_2}
│   │   └── chunks/
│   │       └── {file_id_temp}/
│   │           ├── 000000         # Chunk 0
│   │           ├── 000001         # Chunk 1
│   │           └── 000002         # Chunk 2
│   │
│   └── {user_id_2}/
│       └── ...
│
└── versions/                       # File versions
    └── {file_id}/
        ├── v1
        ├── v2
        └── v3
```

---

## Scalability

### Horizontal Scaling

```
┌─────────────────────────────────────────┐
│         Load Balancer (Nginx/ALB)        │
└─────────────────────────────────────────┘
              │
    ┌─────────┼─────────┬─────────┐
    ▼         ▼         ▼         ▼
┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐
│ API  │  │ API  │  │ API  │  │ API  │
│ Pod 1│  │ Pod 2│  │ Pod 3│  │ Pod N│
└──────┘  └──────┘  └──────┘  └──────┘
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
┌──────┐  ┌──────┐  ┌──────┐
│Redis │  │Postgres│ │MinIO │
│Cluster│ │Primary/│ │Cluster│
│      │  │Replicas│ │      │
└──────┘  └──────┘  └──────┘
```

### Performance Optimization

**Database:**
* Connection pooling (20 connections per pod)
* Read replicas for queries
* Proper indexing on frequently queried fields
* Query optimization with EXPLAIN ANALYZE

**Caching:**
* Redis for session data
* Cache file metadata (5 min TTL)
* Cache user permissions (10 min TTL)

**Storage:**
* CDN for static assets
* S3 Transfer Acceleration
* Multipart upload for large files

**Frontend:**
* Code splitting
* Image optimization
* Lazy loading
* Service worker caching

---

## Monitoring & Observability

### Metrics (Prometheus)

```python
# Request metrics
http_requests_total
http_request_duration_seconds

# Application metrics
file_uploads_total
file_downloads_total
storage_bytes_used
active_users_count

# System metrics
cpu_usage_percent
memory_usage_bytes
disk_io_bytes
```

### Logging

**Structured JSON logs:**

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "logger": "files.router",
  "message": "File uploaded successfully",
  "user_id": "uuid",
  "file_id": "uuid",
  "size_bytes": 1048576,
  "duration_ms": 234
}
```

### Tracing

**Request tracing flow:**

```
Request ID: abc123

├─ API Request (200ms)
│  ├─ Auth Check (10ms)
│  ├─ Database Query (50ms)
│  ├─ Storage Upload (120ms)
│  └─ Response (20ms)
│
└─ Background Task (5s)
   ├─ Celery Queue (100ms)
   └─ Antivirus Scan (4.9s)
```

### Health Checks

```
GET /health
{
  "status": "healthy",
  "components": {
    "database": "healthy",
    "redis": "healthy",
    "storage": "healthy",
    "clamav": "healthy"
  },
  "version": "2.0.0"
}
```

---

## Future Improvements

### Planned Architecture Changes

1. **Microservices**: Split into smaller services
   * Auth Service
   * File Service
   * Storage Service
   * Notification Service

2. **Event-Driven**: Use message queue for events
   * RabbitMQ or Kafka
   * Event sourcing pattern

3. **GraphQL**: Alternative to REST API
   * Better frontend data fetching
   * Reduced over-fetching

4. **Edge Computing**: CDN with edge functions
   * Cloudflare Workers
   * Faster response times

5. **AI/ML**: Intelligent features
   * Auto-tagging files
   * Duplicate detection
   * Smart search

---

**Questions?** Open an issue or ask in our Discord!
