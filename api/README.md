# Feedback Loop API

Cloud backend API for feedback-loop team collaboration platform.

## Overview

This API provides the backend infrastructure for:
- User authentication and authorization
- Pattern synchronization across teams
- Metrics aggregation and analytics
- Team and organization management
- Configuration enforcement

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
# Install dependencies
pip install -e .

# Or install with specific extras
pip install -e ".[test]"
```

### Running the Server

```bash
# Development mode with auto-reload
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Or run directly
python api/main.py
```

The API will be available at:
- http://localhost:8000/api/v1/
- API docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## API Endpoints

### Authentication

#### POST `/api/v1/auth/register`
Register a new user and organization.

**Request:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "secure_password",
  "full_name": "John Doe",
  "organization_name": "Acme Corp"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "admin",
  "organization_id": 1,
  "created_at": "2026-01-07T20:00:00"
}
```

#### POST `/api/v1/auth/login`
Authenticate and receive API key.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "fl_1_abcdef123456...",
  "token_type": "bearer",
  "user_id": 1,
  "organization_id": 1,
  "username": "johndoe",
  "role": "admin"
}
```

#### GET `/api/v1/auth/me`
Get current user information.

**Headers:**
```
Authorization: Bearer fl_1_abcdef123456...
```

**Response:**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "admin",
  "organization_id": 1,
  "created_at": "2026-01-07T20:00:00"
}
```

### Patterns

#### POST `/api/v1/patterns/sync`
Sync patterns to cloud storage.

**Headers:**
```
Authorization: Bearer fl_1_abcdef123456...
```

**Request:**
```json
{
  "patterns": [
    {
      "name": "numpy_json_serialization",
      "description": "Handle NumPy types in JSON",
      "version": 1,
      "category": "serialization"
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "synced_count": 1,
  "conflicts": [],
  "timestamp": "2026-01-07T20:00:00"
}
```

#### GET `/api/v1/patterns/pull`
Pull patterns from cloud storage.

**Headers:**
```
Authorization: Bearer fl_1_abcdef123456...
```

**Response:**
```json
{
  "patterns": [
    {
      "name": "numpy_json_serialization",
      "description": "Handle NumPy types in JSON",
      "version": 2,
      "category": "serialization",
      "last_modified_by": 1,
      "last_modified_at": "2026-01-07T20:00:00"
    }
  ],
  "count": 1,
  "organization_id": 1,
  "timestamp": "2026-01-07T20:00:00"
}
```

### Configuration

#### GET `/api/v1/config`
Get team configuration.

**Headers:**
```
Authorization: Bearer fl_1_abcdef123456...
```

**Response:**
```json
{
  "config": {
    "min_confidence_threshold": 0.8,
    "security_checks_required": true,
    "auto_sync_enabled": true
  },
  "enforced_settings": [
    "security_checks_required",
    "min_confidence_threshold"
  ],
  "team_id": null,
  "organization_id": 1
}
```

#### POST `/api/v1/config`
Update team configuration (admin only).

**Headers:**
```
Authorization: Bearer fl_1_abcdef123456...
```

**Request:**
```json
{
  "min_confidence_threshold": 0.9,
  "security_checks_required": true,
  "auto_sync_enabled": true
}
```

### Metrics

#### POST `/api/v1/metrics`
Submit metrics for analytics.

**Headers:**
```
Authorization: Bearer fl_1_abcdef123456...
```

**Request:**
```json
{
  "metric_type": "pattern_applied",
  "pattern_name": "numpy_json_serialization",
  "time_saved_seconds": 300
}
```

### Admin Endpoints

#### GET `/api/v1/admin/users`
List all users in organization (admin only).

#### DELETE `/api/v1/admin/patterns/{pattern_name}`
Delete a pattern (admin only).

## Database Schema

See `api/models.py` for complete schema definitions.

### Key Models

- **Organization**: Multi-tenant organization with subscription tier
- **Team**: Sub-groups within organizations
- **User**: User accounts with RBAC
- **Pattern**: Versioned development patterns
- **AuditLog**: Immutable audit trail
- **Config**: Team-wide configuration
- **Metric**: Analytics and ROI data

## Security

### Authentication
- API key-based authentication
- Bearer token in Authorization header
- Keys format: `fl_{user_id}_{random_string}`

### Authorization
- Role-Based Access Control (RBAC)
- Roles: admin, developer, viewer
- Admin-only endpoints protected with `require_admin` dependency

### Best Practices
- Use HTTPS in production
- Implement rate limiting
- Use bcrypt/argon2 for password hashing (current implementation is placeholder)
- Rotate API keys regularly
- Enable CORS only for trusted origins

## Development

### Project Structure

```
api/
├── __init__.py       # Package initialization
├── main.py           # FastAPI application and endpoints
├── models.py         # SQLAlchemy database models
└── README.md         # This file
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v
```

### Code Style

Follow PEP 8 and use type hints for better code quality.

## Deployment

### Production Checklist

- [ ] Use PostgreSQL instead of in-memory storage
- [ ] Implement proper password hashing (bcrypt/argon2)
- [ ] Add JWT token authentication
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS for production domains
- [ ] Set up database migrations (Alembic)
- [ ] Add rate limiting middleware
- [ ] Configure logging and monitoring
- [ ] Set up backup strategy
- [ ] Enable database encryption at rest

### Docker Deployment (Coming Soon)

Docker and Helm charts will be provided in Phase 4 for self-hosted deployments.

## Contributing

Contributions are welcome! Please follow the coding standards and add tests for new features.

## License

MIT License - Same as main project.
