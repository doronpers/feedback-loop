# Feedback-Loop - Roadmap & TODOs

**Last Updated**: 2026-01-24
**Single Source of Truth**: This file contains all TODOs, planned features, and roadmap items.

**Note**: This consolidates items from `documentation/PRODUCTION_CHECKLIST.md`. See that file for detailed implementation notes.

---

## ✅ Recently Completed

### Security Improvements (2026-01-24)

1. ✅ **Password Hashing** - Already using bcrypt via passlib CryptContext for secure password hashing
   - **Implementation**: `CryptContext(schemes=["bcrypt"])` with `passlib[bcrypt]>=1.7.4`
   - **Security**: Removed legacy SHA-256 fallback to prevent downgrade attacks
   - **Status**: Production-ready
   - **Completed**: 2026-01-24

2. ✅ **CORS Configuration** - Production-ready CORS configuration with environment-based settings
   - **Features**:
     - Environment variable configuration (`FEEDBACK_LOOP_ALLOWED_ORIGINS`)
     - Secure defaults (localhost only if not configured)
     - Production validation (rejects wildcard, validates URLs)
     - Environment-aware method/header restrictions
     - Comprehensive logging and security warnings
   - **Status**: Production-ready
   - **Completed**: 2026-01-24

### Integration & Dependencies (2026-01-24)

3. ✅ **Partial shared-ai-utils Integration** - Feedback-loop now uses shared-ai-utils for error recovery, metrics, insights, and pattern checks
   - **Status**: Partial integration (with fallbacks for backward compatibility)
   - **Components**: Error recovery framework, metrics collector, insights engine, pattern checks
   - **Note**: Full migration to LLMManager and PatternManager still pending (see item #30)
   - **Completed**: 2026-01-24

---

## 🔴 High Priority - Critical (Must Fix Before Production)

### Data Persistence

#### 1. Database Implementation
- **Status**: 📝 TODO
- **File**: `api/main.py:106-110`
- **Description**: Replace in-memory dictionaries with PostgreSQL
- **Tasks**:
  - Set up SQLAlchemy engine and session management
  - Create database migration scripts with Alembic
  - Configure connection pooling
  - Add database backup strategy

#### 2. CloudSyncClient HTTP Implementation
- **Status**: 📝 TODO
- **Complexity**: Medium
- **Recommended Models**: 1. GPT-5.1-Codex, 2. Claude Sonnet 4.5, 3. Gemini 3 Pro
- **File**: `metrics/sync_client.py:254-255`
- **Description**: Implement actual HTTP requests using `requests` or `httpx`
- **Tasks**:
  - Add retry logic with exponential backoff
  - Handle network errors gracefully
  - Add request/response logging
  - Implement rate limiting

---

## 🟡 Medium Priority - High Priority (Should Fix Soon)

### Authentication

#### 5. JWT Token Support
- **Status**: 📝 TODO
- **Description**: Replace API keys with JWT tokens for better security
- **Tasks**:
  - Add token expiration and refresh logic
  - Implement token revocation

#### 6. Rate Limiting
- **Status**: 📝 TODO
- **Complexity**: Medium
- **Recommended Models**: 1. GPT-5.1-Codex, 2. Claude Sonnet 4.5, 3. Gemini 3 Pro
- **Description**: Add rate limiting middleware to prevent abuse
- **Tasks**:
  - Different limits for authenticated vs unauthenticated requests
  - Consider using Redis for distributed rate limiting

### Configuration

#### 7. Environment Variables
- **Status**: 📝 TODO
- **Description**: Move all configuration to environment variables
- **Tasks**:
  - Support `.env` files for local development
  - Document all required environment variables

#### 8. Secrets Management
- **Status**: 📝 TODO
- **Complexity**: Medium
- **Recommended Models**: 1. GPT-5.1-Codex, 2. Claude Sonnet 4.5, 3. Gemini 3 Pro
- **Description**: Use proper secrets management (AWS Secrets Manager, Vault, etc.)
- **Tasks**:
  - Don't store secrets in code or config files
  - Rotate secrets regularly

### Monitoring & Logging

#### 9. Structured Logging
- **Status**: 📝 TODO
- **Description**: Implement JSON structured logging
- **Tasks**:
  - Add request ID tracking
  - Log all API calls with response times
  - Set up log aggregation (ELK, CloudWatch, etc.)

#### 10. Monitoring & Alerting
- **Status**: 📝 TODO
- **Complexity**: Medium
- **Recommended Models**: 1. GPT-5.1-Codex, 2. Claude Sonnet 4.5, 3. Gemini 3 Pro
- **Description**: Set up health check endpoints and monitoring
- **Tasks**:
  - Monitor API response times
  - Track error rates
  - Set up alerts for critical failures

### Database

#### 11. Database Migrations
- **Status**: 📝 TODO
- **Complexity**: Medium
- **Recommended Models**: 1. GPT-5.1-Codex, 2. Claude Sonnet 4.5, 3. Gemini 3 Pro
- **Description**: Set up Alembic for schema migrations
- **Tasks**:
  - Create initial migration from models
  - Test migration rollback procedures

#### 12. Database Indexes
- **Status**: 📝 TODO
- **Complexity**: Low-Medium
- **Recommended Models**: 1. GPT-5.1-Codex, 2. Claude Sonnet 4.5, 3. Gemini 3 Flash
- **Description**: Add indexes for frequently queried fields
- **Tasks**:
  - Optimize query performance
  - Monitor slow queries

#### 13. Database Encryption
- **Status**: 📝 TODO
- **Description**: Enable encryption at rest and in transit
- **Tasks**:
  - Encrypt sensitive fields (if applicable)
  - Use SSL/TLS for database connections

---

## 🟢 Low Priority - Medium Priority (Nice to Have)

### API Improvements

#### 14. API Documentation
- **Status**: 📝 TODO
- **Complexity**: Low-Medium
- **Recommended Models**: 1. Claude Sonnet 4.5, 2. GPT-5.1, 3. Gemini 3 Flash
- **Description**: Enhance OpenAPI/Swagger documentation
- **Tasks**:
  - Add request/response examples
  - Document error codes and messages

#### 15. API Versioning Strategy
- **Status**: 📝 TODO
- **Description**: Document version deprecation policy
- **Tasks**:
  - Plan for API version lifecycle
  - Add version negotiation

#### 16. Request Validation
- **Status**: 📝 TODO
- **Complexity**: Medium
- **Recommended Models**: 1. GPT-5.1-Codex, 2. Claude Sonnet 4.5, 3. Gemini 3 Pro
- **Description**: Add comprehensive input validation
- **Tasks**:
  - Sanitize user input
  - Validate file uploads

### Performance

#### 17. Caching
- **Status**: 📝 TODO
- **Description**: Add Redis caching for frequently accessed data
- **Tasks**:
  - Cache pattern metadata
  - Implement cache invalidation strategy

#### 18. Connection Pooling
- **Status**: 📝 TODO
- **Complexity**: Low-Medium
- **Recommended Models**: 1. GPT-5.1-Codex, 2. Claude Sonnet 4.5, 3. Gemini 3 Flash
- **Description**: Configure database connection pooling
- **Tasks**:
  - Optimize pool size for workload
  - Monitor connection usage

#### 19. Async Operations
- **Status**: 📝 TODO
- **Description**: Convert blocking operations to async
- **Tasks**:
  - Use async database drivers
  - Implement background task processing

### Testing

#### 20. Integration Tests
- **Status**: 📝 TODO
- **Complexity**: Medium-High
- **Recommended Models**: 1. GPT-5.1-Codex, 2. GPT-5.2-Codex, 3. Claude Sonnet 4.5
- **Description**: Add API endpoint integration tests
- **Tasks**:
  - Test authentication flows
  - Test pattern sync scenarios

#### 21. Load Testing
- **Status**: 📝 TODO
- **Description**: Perform load testing with realistic workloads
- **Tasks**:
  - Identify bottlenecks
  - Test scaling strategy

#### 22. Security Testing
- **Status**: 📝 TODO
- **Complexity**: Medium
- **Recommended Models**: 1. Claude Opus 4.5, 2. GPT-5.2, 3. GPT-5.1-Codex-Max
- **Description**: Perform security audit
- **Tasks**:
  - Test for common vulnerabilities (OWASP Top 10)
  - Implement security scanning in CI/CD

---

## 🔵 Low Priority - Future Enhancements

### Features

#### 23. Webhooks
- **Status**: 📝 TODO
- **Description**: Allow teams to subscribe to pattern updates

#### 24. API Rate Limiting by Tier
- **Status**: 📝 TODO
- **Complexity**: Medium
- **Recommended Models**: 1. GPT-5.1-Codex, 2. Claude Sonnet 4.5, 3. Gemini 3 Pro
- **Description**: Different rate limits for Free/Team/Enterprise tiers

#### 25. Batch Operations
- **Status**: 📝 TODO
- **Description**: Bulk pattern upload/download

### Deployment

#### 26. Docker Image
- **Status**: 📝 TODO
- **Complexity**: Low-Medium
- **Recommended Models**: 1. GPT-5.1-Codex, 2. Claude Sonnet 4.5, 3. Gemini 3 Flash
- **Description**: Create optimized Docker image

#### 27. Kubernetes/Helm
- **Status**: 📝 TODO
- **Description**: Create Kubernetes manifests and Helm chart

#### 28. CI/CD Pipeline
- **Status**: 📝 TODO
- **Complexity**: High
- **Recommended Models**: 1. Claude Opus 4.5, 2. GPT-5.2-Codex, 3. GPT-5.1-Codex-Max
- **Description**: Automated testing and deployment

#### 29. Infrastructure as Code
- **Status**: 📝 TODO
- **Description**: Terraform/CloudFormation templates

### Integration

#### 30. Complete Migration to shared-ai-utils
- **Status**: 📝 TODO (Partial integration complete - see Recently Completed)
- **Complexity**: High
- **Recommended Models**: 1. Claude Opus 4.5, 2. GPT-5.2-Codex, 3. GPT-5.1-Codex-Max
- **Description**: Complete migration to `LLMManager` and `shared_ai_utils.patterns.PatternManager` (currently using shared-ai-utils for error recovery, metrics, insights, and pattern checks with fallbacks)
- **Current State**: Partial integration - shared-ai-utils is a dependency and used for several features, but full LLMManager/PatternManager migration pending
- **Reference**: `council-ai/planning/integration-plan.md`

---

## 📊 Progress Summary

- **Completed**: 3 items
- **High Priority (Critical)**: 2 items (Database Implementation, CloudSyncClient HTTP)
- **Medium Priority (High)**: 9 items
- **Low Priority (Medium)**: 9 items
- **Low Priority (Future)**: 8 items

---

## 📝 Notes

- **Production Checklist**: See `documentation/PRODUCTION_CHECKLIST.md` for detailed implementation notes
- **Security**: See `SECURITY.md` for security best practices
- **Cloud Sync**: See `documentation/CLOUD_SYNC.md` for architecture and usage
- **API Docs**: See `api/README.md` for API documentation

---

## 🔄 How to Update This File

1. When starting work on a TODO, change status from `📝 TODO` to `🚧 In Progress`
2. When completing, move to "Recently Completed" section and mark as `✅`
3. Add new TODOs with complexity indicators (Low, Medium, High) rather than time estimates
4. Update "Last Updated" date
5. Keep items organized by priority and category
