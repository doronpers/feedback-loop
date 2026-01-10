# Cloud Sync & Team Collaboration

**Status:** Phase 1 Implementation In Progress

This document describes the cloud sync and team collaboration features that enable feedback-loop to work as a team platform.

## Overview

The feedback-loop platform is transitioning from a single-user CLI tool to a comprehensive team collaboration platform with cloud sync, analytics, and enterprise features.

## Architecture

### The Bridge: Public & Private Integration

The public repository (open-source CLI tool) contains "hooks" that remain dormant until connected to the private cloud backend:

```
┌─────────────────────────────────────────────────────────────┐
│                     Public Repository                       │
│                  (Open Source CLI Tool)                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────┐       │
│  │  SyncClient (Abstract Base Class)               │       │
│  │  • Provides interface for sync operations        │       │
│  │  • Default: LocalSyncClient (file system)       │       │
│  │  • When logged in: CloudSyncClient (API)        │       │
│  └─────────────────────────────────────────────────┘       │
│                                                             │
│  ┌─────────────────────────────────────────────────┐       │
│  │  MetricsIntegration                              │       │
│  │  • Accepts optional sync_client parameter        │       │
│  │  • Swaps clients based on authentication         │       │
│  └─────────────────────────────────────────────────┘       │
│                                                             │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ When user runs: feedback-loop login
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    Cloud Backend API                        │
│                  (Private Repository)                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  • Authentication & Authorization (JWT/API Keys)            │
│  • Pattern Synchronization (Bi-directional)                 │
│  • Team Management (Organizations, Teams, Users)            │
│  • Analytics & Metrics Aggregation                          │
│  • Configuration Management (Enforced Settings)             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Phase 1: Infrastructure & Authentication

### 1.1 Centralized API Gateway (FastAPI)

**Status:** ✅ Implemented

Location: `api/main.py`

The API gateway provides RESTful endpoints for:

- Authentication (`/api/v1/auth/login`, `/api/v1/auth/register`)
- Pattern synchronization (`/api/v1/patterns/sync`, `/api/v1/patterns/pull`)
- Configuration management (`/api/v1/config`)
- Metrics submission (`/api/v1/metrics`)
- Admin operations (`/api/v1/admin/*`)

**Key Features:**

- API versioning (`/api/v1/`)
- Bearer token authentication
- CORS support for web dashboard
- Request validation with Pydantic

**Configuration Notes:**

- `FEEDBACK_LOOP_ALLOWED_ORIGINS` (comma-separated) controls CORS origins.
- Passwords are stored with PBKDF2 hashing in the in-memory store.

### 1.2 User & Organization Management

**Status:** ✅ Schema Implemented

Location: `api/models.py`

Database models for:

- **Organizations**: Multi-tenant architecture with subscription tiers
- **Teams**: Sub-groups within organizations
- **Users**: Authentication, RBAC, SSO support
- **Patterns**: Versioned pattern storage with team sharing
- **AuditLog**: Immutable audit trail for compliance

**RBAC Roles:**

- `ADMIN`: Can delete patterns, manage team, view analytics
- `DEVELOPER`: Can read/write patterns
- `VIEWER`: Read-only access

**Subscription Tiers:**

- `FREE`: Single-user, local only
- `TEAM`: $25/user/month - Team sync and basic analytics
- `ENTERPRISE`: $50+/user/month - SSO, compliance, self-hosted

### 1.3 SyncClient Abstraction

**Status:** ✅ Implemented

Location: `metrics/sync_client.py`

The `SyncClient` provides an abstraction layer for synchronization:

```python
# Default: Local file system
client = LocalSyncClient(
    patterns_file="patterns.json",
    metrics_file="metrics_data.json"
)

# After login: Cloud sync
client = CloudSyncClient(
    api_url="https://api.feedback-loop.dev",
    api_key="fl_user123_...",
    organization_id="org1",
    team_id="team1"
)
```

**Operations:**

- `sync_patterns()`: Push patterns to storage
- `pull_patterns()`: Pull patterns from storage
- `sync_metrics()`: Push metrics for analytics
- `pull_config()`: Get team-enforced configuration

## Usage

### For End Users

#### Login to Cloud Backend

```bash
# Login to enable cloud sync
feedback-loop login

# Or specify custom API URL
feedback-loop login --api-url https://api.example.com
```

The login command will:

1. Prompt for email and password
2. Authenticate with the cloud API
3. Save credentials to `~/.feedback-loop/auth.json`
4. Enable cloud sync for all subsequent commands

#### Using Cloud Sync

Once logged in, all pattern and metrics operations automatically sync:

```bash
# Patterns automatically sync to team
feedback-loop analyze

# Metrics are aggregated for analytics
feedback-loop collect

# Pull team-enforced configuration
feedback-loop generate "Create a safe file handler"
```

### For Developers

#### Using SyncClient Directly

```python
from metrics.sync_client import create_sync_client

# Create local client (default)
client = create_sync_client(use_cloud=False)

# Create cloud client (if authenticated)
client = create_sync_client(
    use_cloud=True,
    api_url="https://api.example.com",
    api_key="your_api_key"
)

# Sync patterns
patterns = [{"name": "pattern1", "description": "..."}]
result = client.sync_patterns(patterns)
print(result)  # {"status": "success", "synced_count": 1, ...}

# Pull patterns
patterns = client.pull_patterns()
```

#### Integrating with MetricsIntegration

```python
from metrics.integrate import MetricsIntegration
from metrics.sync_client import CloudSyncClient

# Create cloud sync client
sync_client = CloudSyncClient(
    api_url="https://api.example.com",
    api_key="your_api_key"
)

# Use with MetricsIntegration
integration = MetricsIntegration(
    sync_client=sync_client
)

integration.analyze_metrics(update_patterns=True)
```

## Running the API Server

### Development

Start the API server locally for testing:

```bash
cd api
python main.py

# Or use uvicorn directly with auto-reload
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Environment Variables** (all optional):

```bash
# CORS configuration (comma-separated origins)
export FEEDBACK_LOOP_ALLOWED_ORIGINS="http://localhost:3000,http://localhost:5173"

# Password hashing iterations (default: 210000, minimum: 100000)
export FEEDBACK_LOOP_PASSWORD_ITERATIONS=210000
```

The API will be available at:

- Endpoints: <http://localhost:8000/api/v1/>
- Interactive docs: <http://localhost:8000/api/docs>
- ReDoc: <http://localhost:8000/api/redoc>

### Production

For production deployment, see the deployment guide in `docs/DEPLOYMENT.md` (coming soon).

## Security

For comprehensive security guidelines including API key management, data privacy, and best practices, see [SECURITY.md](../SECURITY.md).

**Quick Notes:**

- API keys use Bearer token authentication
- Passwords hashed with PBKDF2-HMAC-SHA256 (210,000 iterations)
- CORS configured via `FEEDBACK_LOOP_ALLOWED_ORIGINS` environment variable
- All code is open source and can be self-hosted for maximum data control

## Testing

Run the sync client tests:

```bash
# Run sync client tests
pytest tests/test_sync_client.py -v

# Run all tests
pytest tests/ -v
```

## Roadmap

### Phase 1: Infrastructure & Authentication ✅ (Current)

- [x] Centralized API Gateway
- [x] User & Organization Management schemas
- [x] SyncClient abstraction
- [x] Login command
- [ ] Database implementation (PostgreSQL)
- [ ] Proper password hashing (bcrypt)
- [ ] JWT token authentication
- [ ] Encrypted pattern storage

### Phase 2: Team Sync Engine (Next)

- [ ] Bi-directional pattern sync
- [ ] Conflict resolution
- [ ] Pattern versioning
- [ ] Shared configuration management
- [ ] Real-time sync updates

### Phase 3: Analytics & ROI Dashboard

- [ ] React/Vite frontend
- [ ] Time saved calculations
- [ ] ROI metrics visualization
- [ ] Personalized fulfillment metrics

### Phase 4: Enterprise & Compliance

- [ ] SSO/SAML integration (Okta, AzureAD)
- [ ] Immutable audit logging
- [ ] Compliance reporting
- [ ] Docker/Helm charts for self-hosted deployment

## Contributing

This is Phase 1 of a multi-phase implementation. Contributions are welcome!

See the main implementation plan in the PR description for the full roadmap.

## License

Same as main project (MIT).
