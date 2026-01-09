# Database Configuration & Data Sources for Superset Integration

This document provides a comprehensive overview of all databases and data sources configured in the doronpers/feedback-loop repository that can be connected to Apache Superset for analytics and visualization.

## Table of Contents

- [Overview](#overview)
- [Database Systems](#database-systems)
- [Data Source 1: Metrics Database](#data-source-1-metrics-database)
- [Data Source 2: API Database](#data-source-2-api-database)
- [External Data Integrations](#external-data-integrations)
- [Superset Connection Guide](#superset-connection-guide)
- [Data Source Comparison](#data-source-comparison)
- [Security & Access Control](#security--access-control)
- [Performance Considerations](#performance-considerations)

---

## Overview

The feedback-loop system uses **two primary databases** that can be connected to Superset:

1. **Metrics Database** - Time-series metrics for code quality, patterns, and AI-assisted development
2. **API Database** - User management, pattern library, teams, and audit logs

Both databases support:
- **SQLite** for local development and testing
- **PostgreSQL** for production deployments
- **Cloud database providers** (AWS RDS, Google Cloud SQL, Azure Database, Heroku)

---

## Database Systems

### Supported Databases

| Database | Status | Use Case | Notes |
|----------|--------|----------|-------|
| **SQLite** | ✅ Fully Supported | Local development | Default, no setup required |
| **PostgreSQL** | ✅ Fully Supported | Production | Recommended for teams |
| **MySQL** | ⚠️ Untested | Potential | Would require driver installation |
| **Oracle** | ⚠️ Untested | Enterprise | Would require driver installation |
| **Microsoft SQL Server** | ⚠️ Untested | Enterprise | Would require driver installation |

### ORM Framework

- **SQLAlchemy 2.x** - Used for all database operations
- **Connection pooling** - Supported for production deployments
- **Migration support** - Tables auto-created via `Base.metadata.create_all()`

---

## Data Source 1: Metrics Database

### Purpose

Stores time-series metrics data collected from:
- Test execution (pytest with `--enable-metrics`)
- Code generation events
- Bug detection
- Code review findings
- Performance measurements
- Deployment issues

### Database Schema

Located in: `superset-dashboards/database/models.py`

#### Tables Overview

| Table Name | Records | Purpose | Key Fields |
|------------|---------|---------|------------|
| `metrics_bugs` | Bug occurrences | Track detected bugs with pattern correlation | pattern, error, file_path, timestamp |
| `metrics_test_failures` | Test failures | Record test failures and pattern violations | test_name, pattern_violated, timestamp |
| `metrics_code_reviews` | Code review issues | Store code review findings by severity | issue_type, pattern, severity, timestamp |
| `metrics_performance` | Performance data | Track execution time, memory usage | metric_type, execution_time_ms, memory_usage_bytes |
| `metrics_deployment` | Deployment issues | Record production deployment problems | issue_type, environment, resolution_time_minutes |
| `metrics_code_generation` | AI code gen events | Track AI-assisted code generation | prompt, patterns_applied, confidence, success |
| `pattern_effectiveness` | Pattern metrics | Aggregate pattern success rates over time | pattern_name, effectiveness_score, period_start |
| `metrics_summary` | Pre-computed stats | Daily/weekly summary statistics | metric_type, summary_date, trend_direction |

#### Detailed Table Schemas

##### 1. metrics_bugs
```sql
CREATE TABLE metrics_bugs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern VARCHAR(255) NOT NULL,              -- Pattern name that detected the bug
    error TEXT NOT NULL,                        -- Error message
    code TEXT,                                  -- Code snippet
    file_path VARCHAR(500),                     -- File where bug occurred
    line INTEGER,                               -- Line number
    stack_trace TEXT,                           -- Full stack trace
    count INTEGER DEFAULT 1,                    -- Occurrence count
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_bug_pattern_timestamp ON metrics_bugs(pattern, timestamp);
CREATE INDEX idx_bug_file_path ON metrics_bugs(file_path);
```

**Key Analytics:**
- Bug trends by pattern over time
- Most affected files/modules
- Bug recurrence analysis
- Pattern correlation with bugs

##### 2. metrics_test_failures
```sql
CREATE TABLE metrics_test_failures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_name VARCHAR(500) NOT NULL,            -- Test function name
    failure_reason TEXT NOT NULL,               -- Why test failed
    pattern_violated VARCHAR(255),              -- Pattern that was violated
    code_snippet TEXT,                          -- Failed code
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_test_pattern_timestamp ON metrics_test_failures(pattern_violated, timestamp);
```

**Key Analytics:**
- Test failure rates over time
- Most fragile tests
- Pattern violation frequency
- Failure reason categorization

##### 3. metrics_code_reviews
```sql
CREATE TABLE metrics_code_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_type VARCHAR(255) NOT NULL,           -- Type of issue found
    pattern VARCHAR(255) NOT NULL,              -- Related pattern
    severity VARCHAR(50) NOT NULL,              -- high, medium, low
    file_path VARCHAR(500),                     -- File with issue
    line INTEGER,                               -- Line number
    suggestion TEXT,                            -- Suggested fix
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_review_pattern_severity ON metrics_code_reviews(pattern, severity);
CREATE INDEX idx_review_timestamp ON metrics_code_reviews(timestamp);
```

**Key Analytics:**
- Code quality trends
- High-severity issue tracking
- Pattern-based issue distribution
- Reviewer effectiveness

##### 4. metrics_performance
```sql
CREATE TABLE metrics_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_type VARCHAR(100) NOT NULL,          -- Type of performance metric
    details JSON,                               -- Full metric details
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Extracted fields for easier querying
    function_name VARCHAR(255),                 -- Function being measured
    execution_time_ms FLOAT,                    -- Execution time in milliseconds
    memory_usage_bytes INTEGER,                 -- Memory usage
    file_size_bytes INTEGER                     -- File size if applicable
);

-- Indexes
CREATE INDEX idx_perf_type_timestamp ON metrics_performance(metric_type, timestamp);
```

**Key Analytics:**
- Performance bottleneck identification
- Execution time trends
- Memory usage patterns
- Function-level performance

##### 5. metrics_deployment
```sql
CREATE TABLE metrics_deployment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_type VARCHAR(255) NOT NULL,           -- Type of deployment issue
    pattern VARCHAR(255),                       -- Related pattern
    environment VARCHAR(50) NOT NULL,           -- production, staging, dev
    root_cause TEXT,                            -- Root cause analysis
    resolution_time_minutes INTEGER,            -- Time to resolve
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_deploy_env_timestamp ON metrics_deployment(environment, timestamp);
CREATE INDEX idx_deploy_pattern ON metrics_deployment(pattern);
```

**Key Analytics:**
- Deployment success rate by environment
- Mean time to recovery (MTTR)
- Issue type distribution
- Pattern correlation with deployments

##### 6. metrics_code_generation (The "Fusion Engine")
```sql
CREATE TABLE metrics_code_generation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt TEXT NOT NULL,                       -- User's generation prompt
    patterns_applied JSON,                      -- List of patterns used
    confidence FLOAT NOT NULL,                  -- AI confidence score (0.0-1.0)
    success BOOLEAN NOT NULL,                   -- Generation succeeded?
    code_length INTEGER,                        -- Length of generated code
    compilation_error TEXT,                     -- Error if failed
    generation_metadata JSON,                   -- Additional metadata
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    patterns_count INTEGER                      -- Number of patterns applied
);

-- Indexes
CREATE INDEX idx_generation_success_timestamp ON metrics_code_generation(success, timestamp);
CREATE INDEX idx_generation_confidence ON metrics_code_generation(confidence);
```

**Key Analytics (Fusion Engine):**
- Code generation success rate over time
- Average confidence scores (sensor confidence)
- Pattern fusion analysis (which patterns work together)
- Failure pattern analysis
- Code complexity metrics

##### 7. pattern_effectiveness
```sql
CREATE TABLE pattern_effectiveness (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_name VARCHAR(255) NOT NULL,         -- Pattern identifier
    application_count INTEGER DEFAULT 0,        -- Times applied
    success_count INTEGER DEFAULT 0,            -- Successful applications
    failure_count INTEGER DEFAULT 0,            -- Failed applications
    effectiveness_score FLOAT,                  -- 0.0 to 1.0
    period_start DATETIME NOT NULL,             -- Period start
    period_end DATETIME NOT NULL                -- Period end
);

-- Indexes
CREATE INDEX idx_pattern_eff_name_period ON pattern_effectiveness(pattern_name, period_start);
```

**Key Analytics:**
- Pattern ROI calculation
- Effectiveness trends over time
- Success/failure ratio by pattern
- Pattern lifecycle analysis

##### 8. metrics_summary
```sql
CREATE TABLE metrics_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_type VARCHAR(100) NOT NULL,          -- Type of summary
    summary_date DATETIME NOT NULL,             -- Date of summary
    
    -- Summary counts
    total_count INTEGER DEFAULT 0,
    high_severity_count INTEGER DEFAULT 0,
    medium_severity_count INTEGER DEFAULT 0,
    low_severity_count INTEGER DEFAULT 0,
    
    -- Pattern statistics
    top_pattern VARCHAR(255),                   -- Most frequent pattern
    top_pattern_count INTEGER,
    
    -- Trends
    trend_direction VARCHAR(20),                -- increasing, decreasing, stable
    week_over_week_change FLOAT                 -- % change
);

-- Indexes
CREATE INDEX idx_summary_type_date ON metrics_summary(metric_type, summary_date);
```

**Key Analytics:**
- Weekly/monthly trend analysis
- Top pattern identification
- Aggregated KPIs
- Historical comparison

### Connection Configuration

#### SQLite (Development)

**File Location:** `sample_metrics.db` (in repository root)

**SQLAlchemy URI:**
```
sqlite:////absolute/path/to/feedback-loop/sample_metrics.db
```

**Example:**
```python
from sqlalchemy import create_engine

db_path = '/home/user/feedback-loop/sample_metrics.db'
engine = create_engine(f'sqlite:///{db_path}')
```

**Superset Configuration:**
1. Go to **Settings → Database Connections → + Database**
2. Select **SQLite**
3. Enter URI: `sqlite:////home/user/feedback-loop/sample_metrics.db`
4. Test connection
5. Click **Connect**

#### PostgreSQL (Production)

**Default Database Name:** `feedback_loop`

**SQLAlchemy URI:**
```
postgresql://username:password@hostname:5432/feedback_loop
```

**Docker Setup:**
```bash
docker run -d \
  --name feedback-postgres \
  -e POSTGRES_DB=feedback_loop \
  -e POSTGRES_USER=feedback_user \
  -e POSTGRES_PASSWORD=secure_password \
  -p 5432:5432 \
  postgres:14
```

**Connection URI:**
```
postgresql://feedback_user:secure_password@localhost:5432/feedback_loop
```

**Superset Configuration:**
1. Go to **Settings → Database Connections → + Database**
2. Select **PostgreSQL**
3. Enter connection details:
   - Host: `localhost` (or server hostname)
   - Port: `5432`
   - Database: `feedback_loop`
   - Username: `feedback_user`
   - Password: `secure_password`
4. Test connection
5. Click **Connect**

### Data Export Process

**Script:** `superset-dashboards/scripts/export_to_db.py`

**Usage:**
```bash
# Export to SQLite
python superset-dashboards/scripts/export_to_db.py \
  --format sqlite \
  --input metrics_data.json

# Export to PostgreSQL
python superset-dashboards/scripts/export_to_db.py \
  --format postgresql \
  --db-uri "postgresql://user:pass@localhost:5432/feedback_loop" \
  --input metrics_data.json
```

**Automated Sync:**
```bash
# Configure sync
cp superset-dashboards/scripts/sync_config.example.json sync_config.json
# Edit sync_config.json with your database URI

# Run sync manually
python superset-dashboards/scripts/sync_metrics.py --config sync_config.json

# Or set up cron job (every hour)
0 * * * * cd /path/to/feedback-loop && python superset-dashboards/scripts/sync_metrics.py
```

### Sample Data

**File:** `sample_metrics.db` (156KB)
**Contains:** Pre-populated sample data for testing dashboards

**Tables populated:**
- ✅ metrics_bugs (sample bug records)
- ✅ metrics_test_failures (sample test failures)
- ✅ metrics_code_reviews (sample review issues)
- ✅ metrics_performance (sample performance data)
- ✅ metrics_deployment (sample deployment issues)
- ✅ metrics_code_generation (sample AI generation events)
- ✅ pattern_effectiveness (sample pattern metrics)
- ✅ metrics_summary (sample summaries)

---

## Data Source 2: API Database

### Purpose

Stores operational data for the feedback-loop platform:
- User accounts and authentication
- Organizations and teams (multi-tenancy)
- Pattern library with versioning
- Audit logs for compliance
- User/team metrics with ROI data

### Database Schema

Located in: `api/models.py`

#### Tables Overview

| Table Name | Purpose | Key Fields |
|------------|---------|------------|
| `organizations` | Multi-tenant organizations | name, slug, subscription_tier |
| `teams` | Teams within organizations | name, organization_id, settings |
| `users` | User accounts | email, username, role, organization_id |
| `user_teams` | User-team membership | user_id, team_id, role |
| `patterns` | Pattern library | name, category, severity, effectiveness_score |
| `audit_logs` | Compliance audit trail | action, resource_type, user_id, timestamp |
| `configs` | Team configuration | key, value, is_enforced |
| `metrics` | User/team metrics | metric_type, time_saved_seconds, pattern_id |

#### Detailed Table Schemas

##### 1. organizations
```sql
CREATE TABLE organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    subscription_tier VARCHAR(20) DEFAULT 'free',  -- free, team, enterprise
    settings JSON,                                 -- Org-wide settings
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Key Analytics:**
- Organization count by subscription tier
- Usage patterns by tier
- Growth metrics

##### 2. teams
```sql
CREATE TABLE teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    description TEXT,
    settings JSON,                                 -- Team-specific settings
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);
```

**Key Analytics:**
- Team size distribution
- Team activity levels
- Cross-team collaboration

##### 3. users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    api_key VARCHAR(255) UNIQUE,
    full_name VARCHAR(255),
    avatar_url VARCHAR(500),
    role VARCHAR(20) DEFAULT 'developer',          -- admin, developer, viewer
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    sso_provider VARCHAR(50),                      -- okta, azure_ad, etc.
    sso_id VARCHAR(255),
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);
```

**Key Analytics:**
- User activity (last_login)
- Role distribution
- SSO adoption rate
- User growth over time

##### 4. patterns
```sql
CREATE TABLE patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    team_id INTEGER,
    author_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100),
    severity VARCHAR(50),                          -- low, medium, high, critical
    pattern_data JSON NOT NULL,                    -- Full pattern details
    code_example TEXT,
    solution TEXT,
    frequency INTEGER DEFAULT 0,
    effectiveness_score INTEGER DEFAULT 0,
    times_applied INTEGER DEFAULT 0,
    version INTEGER DEFAULT 1,
    parent_id INTEGER,                             -- For versioning
    is_active BOOLEAN DEFAULT TRUE,
    is_archived BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_applied DATETIME,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (team_id) REFERENCES teams(id),
    FOREIGN KEY (author_id) REFERENCES users(id),
    FOREIGN KEY (parent_id) REFERENCES patterns(id)
);
```

**Key Analytics:**
- Pattern library growth
- Most effective patterns by category
- Pattern adoption rate
- Version history analysis
- Author contribution metrics

##### 5. audit_logs
```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,                  -- create, update, delete, login, etc.
    resource_type VARCHAR(100) NOT NULL,           -- pattern, user, team, etc.
    resource_id INTEGER,
    old_values JSON,                               -- Before state
    new_values JSON,                               -- After state
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Indexes
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_timestamp ON audit_logs(created_at);
```

**Key Analytics (SAR-equivalent):**
- Complete audit trail for compliance
- User action history
- Change tracking (before/after)
- Security event monitoring
- Compliance reporting

##### 6. metrics (User/Team Metrics)
```sql
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    team_id INTEGER,
    user_id INTEGER,
    metric_type VARCHAR(100) NOT NULL,             -- pattern_applied, bug_found, etc.
    metric_data JSON NOT NULL,
    time_saved_seconds INTEGER DEFAULT 0,          -- For ROI calculation
    pattern_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (team_id) REFERENCES teams(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (pattern_id) REFERENCES patterns(id)
);

-- Indexes
CREATE INDEX idx_metrics_type ON metrics(metric_type);
CREATE INDEX idx_metrics_timestamp ON metrics(created_at);
```

**Key Analytics:**
- ROI per user/team/pattern
- Time saved calculations
- Pattern usage by user
- Team productivity metrics

### Connection Configuration

The API database is configured similarly to the Metrics database:

**Development (SQLite):**
```
sqlite:////absolute/path/to/feedback-loop/api.db
```

**Production (PostgreSQL):**
```
postgresql://username:password@hostname:5432/feedback_loop_api
```

**Note:** For production deployments, you may want to use separate databases:
- `feedback_loop_metrics` - For time-series metrics data
- `feedback_loop_api` - For operational/transactional data

Or use a single database with schema separation:
- `metrics` schema - For metrics tables
- `api` schema - For API tables

---

## External Data Integrations

### 1. GitHub Actions Integration

**File:** `superset-dashboards/examples/github-actions-metrics.yml`

**Purpose:** Collect CI/CD metrics from GitHub Actions workflows

**Data Collected:**
- Workflow run duration
- Test pass/fail rates
- Build success rates
- Deployment frequency

**Integration Method:**
```yaml
# .github/workflows/metrics.yml
- name: Collect Metrics
  run: pytest --enable-metrics

- name: Export to Database
  run: python superset-dashboards/scripts/export_to_db.py --format postgresql
  env:
    METRICS_DB_URI: ${{ secrets.METRICS_DB_URI }}
```

### 2. JSON File Export

**Default:** `metrics_data.json` (local file)

**Format:**
```json
{
  "bugs": [...],
  "test_failures": [...],
  "code_reviews": [...],
  "performance_metrics": [...],
  "deployment_issues": [...],
  "code_generation": [...]
}
```

**Usage:** Intermediate format before database export

### 3. Potential Future Integrations

These are NOT currently implemented but could be added:

- **Jira**: Import issue tracking data
- **Slack**: Activity metrics
- **Datadog/New Relic**: Application performance monitoring
- **Sentry**: Error tracking integration
- **Git**: Commit analysis and code churn metrics
- **SonarQube**: Code quality metrics
- **Jenkins/CircleCI**: CI/CD metrics from other platforms

---

## Superset Connection Guide

### Multi-Database Setup in Superset

To connect both databases to Superset for comprehensive analytics:

#### Step 1: Add Metrics Database

```
1. Navigate to: Settings → Database Connections → + Database
2. Database Name: "Feedback Loop Metrics"
3. SQLAlchemy URI: <your metrics database URI>
4. Test Connection
5. Advanced → Expose in SQL Lab: ✓
6. Save
```

#### Step 2: Add API Database (Optional)

```
1. Navigate to: Settings → Database Connections → + Database
2. Database Name: "Feedback Loop API"
3. SQLAlchemy URI: <your API database URI>
4. Test Connection
5. Advanced → Expose in SQL Lab: ✓
6. Save
```

#### Step 3: Create Datasets

For each table you want to visualize:

```
1. Navigate to: Data → Datasets → + Dataset
2. Select database
3. Select schema (if applicable)
4. Select table
5. Save
```

**Recommended Priority:**
- ✅ metrics_code_generation (Fusion Engine analytics)
- ✅ pattern_effectiveness (Pattern confidence scores)
- ✅ metrics_bugs (Detection results)
- ✅ metrics_code_reviews (Detection results)
- ✅ audit_logs (SAR-equivalent reporting)
- ✅ patterns (Pattern library)

#### Step 4: Configure Virtual Datasets (Optional)

Create virtual datasets for complex queries:

**Example: Pattern ROI Analysis**
```sql
SELECT 
  p.name as pattern_name,
  p.category,
  p.times_applied,
  AVG(pe.effectiveness_score) as effectiveness,
  SUM(m.time_saved_seconds) / 3600.0 as hours_saved,
  COUNT(DISTINCT m.user_id) as users_benefited
FROM patterns p
LEFT JOIN metrics m ON m.pattern_id = p.id
LEFT JOIN pattern_effectiveness pe ON pe.pattern_name = p.name
WHERE p.is_active = true
GROUP BY p.id, p.name, p.category, p.times_applied
```

---

## Data Source Comparison

### Metrics Database vs API Database

| Feature | Metrics Database | API Database |
|---------|------------------|--------------|
| **Purpose** | Analytics & reporting | Operations & management |
| **Data Type** | Time-series events | Transactional data |
| **Update Frequency** | Continuous (during tests/builds) | On user actions |
| **Retention** | Historical (years) | Current state + audit logs |
| **Query Pattern** | Aggregations, trends | Lookups, joins |
| **Superset Use** | Dashboards, charts | Reference data, drill-downs |
| **Size Growth** | Grows continuously | Grows with users |

### When to Use Which

**Use Metrics Database for:**
- ✅ Time-series visualizations
- ✅ Trend analysis
- ✅ KPI monitoring
- ✅ Code generation success rates (Fusion Engine)
- ✅ Pattern effectiveness over time (Confidence scores)
- ✅ Bug/test failure trends (Detection results)

**Use API Database for:**
- ✅ User/team dashboards
- ✅ Pattern library exploration
- ✅ Audit trail reporting (SAR-equivalent)
- ✅ ROI calculations per pattern/user
- ✅ Organization/team analytics
- ✅ Compliance reporting

**Join Both for:**
- ✅ Comprehensive pattern ROI (pattern library + time saved metrics)
- ✅ User productivity analysis (users + their metrics)
- ✅ Team effectiveness (teams + their generated metrics)

---

## Security & Access Control

### Database Security Best Practices

#### 1. Connection Security

**Use SSL/TLS for PostgreSQL:**
```
postgresql://user:pass@host:5432/db?sslmode=require
```

**For Production:**
- Always use `sslmode=require`
- Use certificate verification when possible
- Never commit connection strings to git
- Use environment variables or secret managers

#### 2. User Permissions

**Superset Database User (Read-Only):**
```sql
-- Create read-only user for Superset
CREATE USER superset_viewer WITH PASSWORD 'secure_password';

-- Grant SELECT only on metrics database
GRANT CONNECT ON DATABASE feedback_loop TO superset_viewer;
GRANT USAGE ON SCHEMA public TO superset_viewer;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO superset_viewer;

-- For future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
  GRANT SELECT ON TABLES TO superset_viewer;
```

#### 3. Row-Level Security (Optional)

For multi-tenant Superset instances:

```sql
-- Enable RLS on patterns table
ALTER TABLE patterns ENABLE ROW LEVEL SECURITY;

-- Policy: users can only see their organization's patterns
CREATE POLICY org_isolation ON patterns
  FOR SELECT
  USING (organization_id = current_setting('app.current_org_id')::INTEGER);
```

#### 4. Environment Variables

**Example `.env` file (DO NOT commit):**
```bash
# Metrics Database
METRICS_DB_URI=postgresql://metrics_user:pass123@db.example.com:5432/feedback_loop

# API Database
API_DB_URI=postgresql://api_user:pass456@db.example.com:5432/feedback_loop_api

# Superset Credentials (for automated dashboard import)
SUPERSET_URL=https://superset.example.com
SUPERSET_USERNAME=admin
SUPERSET_PASSWORD=admin_pass
```

---

## Performance Considerations

### 1. Index Strategy

**Already Implemented Indexes:**

Metrics Database:
```sql
-- metrics_bugs
idx_bug_pattern_timestamp (pattern, timestamp)
idx_bug_file_path (file_path)

-- metrics_code_generation
idx_generation_success_timestamp (success, timestamp)
idx_generation_confidence (confidence)

-- pattern_effectiveness
idx_pattern_eff_name_period (pattern_name, period_start)

-- And more... (see models.py)
```

**Additional Indexes for Heavy Queries:**
```sql
-- If querying by date range frequently
CREATE INDEX idx_metrics_bugs_timestamp ON metrics_bugs(timestamp DESC);
CREATE INDEX idx_code_gen_timestamp ON metrics_code_generation(timestamp DESC);

-- If grouping by pattern often
CREATE INDEX idx_metrics_bugs_pattern ON metrics_bugs(pattern);

-- For JSON field queries (PostgreSQL)
CREATE INDEX idx_code_gen_patterns_gin ON metrics_code_generation 
  USING GIN (patterns_applied jsonb_path_ops);
```

### 2. Partitioning (PostgreSQL)

For large datasets (millions of records), consider partitioning:

```sql
-- Partition metrics_code_generation by month
CREATE TABLE metrics_code_generation_y2024m01 
  PARTITION OF metrics_code_generation
  FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE metrics_code_generation_y2024m02 
  PARTITION OF metrics_code_generation
  FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Etc...
```

### 3. Materialized Views

Create pre-aggregated views for complex dashboards:

```sql
-- Create materialized view for daily pattern statistics
CREATE MATERIALIZED VIEW daily_pattern_stats AS
SELECT 
  DATE_TRUNC('day', timestamp) as day,
  pattern,
  COUNT(*) as bug_count,
  AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate
FROM metrics_bugs
GROUP BY DATE_TRUNC('day', timestamp), pattern;

-- Create index on materialized view
CREATE INDEX idx_daily_pattern_stats_day ON daily_pattern_stats(day DESC);

-- Refresh daily
REFRESH MATERIALIZED VIEW daily_pattern_stats;
```

**Refresh Schedule (pg_cron):**
```sql
SELECT cron.schedule(
  'refresh-daily-stats',
  '0 1 * * *',  -- 1 AM daily
  'REFRESH MATERIALIZED VIEW daily_pattern_stats'
);
```

### 4. Query Optimization Tips

**Use EXPLAIN ANALYZE:**
```sql
EXPLAIN ANALYZE
SELECT pattern, COUNT(*) 
FROM metrics_bugs 
WHERE timestamp > NOW() - INTERVAL '30 days'
GROUP BY pattern;
```

**Limit Large Datasets:**
```python
# In Superset chart config
{
  "row_limit": 1000,
  "time_range": "Last 30 days"
}
```

**Use Result Caching:**
```python
# Superset dashboard settings
{
  "cache_timeout": 300,  # 5 minutes
  "refresh_frequency": 60  # Check every minute
}
```

### 5. Connection Pooling

**Production Configuration:**
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'postgresql://user:pass@host:5432/feedback_loop',
    poolclass=QueuePool,
    pool_size=10,          # Keep 10 connections open
    max_overflow=20,       # Allow up to 30 total connections
    pool_pre_ping=True,    # Verify connections before use
    pool_recycle=3600      # Recycle connections after 1 hour
)
```

---

## Summary

### Databases Available

1. **Metrics Database** (Primary for Superset)
   - ✅ 8 tables with time-series metrics
   - ✅ Pre-populated sample data available
   - ✅ Optimized indexes for analytics
   - ✅ SQLite (dev) and PostgreSQL (prod) support

2. **API Database** (Secondary for Superset)
   - ✅ 8 tables with operational data
   - ✅ Multi-tenancy support
   - ✅ Audit logging for compliance
   - ✅ Pattern library with versioning

### Connection URIs

**SQLite (Development):**
```
sqlite:////absolute/path/to/feedback-loop/sample_metrics.db
```

**PostgreSQL (Production):**
```
postgresql://username:password@hostname:5432/feedback_loop
```

### Key Superset Use Cases

1. **Fusion Engine Monitoring** → `metrics_code_generation` table
2. **Confidence Scoring** → `metrics_code_generation.confidence` + `pattern_effectiveness` table
3. **Detection Results** → `metrics_bugs`, `metrics_test_failures`, `metrics_code_reviews` tables
4. **SAR Reporting** → `audit_logs` table + `metrics_summary` table

### Next Steps

1. ✅ Connect Superset to `sample_metrics.db` for testing
2. ✅ Import pre-configured dashboards
3. ✅ Configure PostgreSQL for production
4. ✅ Set up automated sync with `sync_metrics.py`
5. ✅ Create custom dashboards using SQL Lab
6. ✅ Configure alerts for critical metrics

---

## References

- [Database Models](database/models.py)
- [API Models](../api/models.py)
- [Connection Examples](database/connection_examples.md)
- [Export Script](scripts/export_to_db.py)
- [Sync Script](scripts/sync_metrics.py)
- [Superset Integration Guide](../docs/SUPERSET_INTEGRATION.md)
- [Dashboard Design Recommendations](DASHBOARD_DESIGN_RECOMMENDATIONS.md)
