# Apache Superset Integration Guide

Complete guide for integrating Apache Superset with feedback-loop for powerful metrics visualization and analytics.

## Table of Contents

1. [Overview](#overview)
2. [Why Superset?](#why-superset)
3. [Architecture](#architecture)
4. [Setup Guide](#setup-guide)
5. [Dashboard Workflows](#dashboard-workflows)
6. [Advanced Usage](#advanced-usage)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Overview

This integration enables feedback-loop to export its collected metrics to a SQL database that Apache Superset can query and visualize. The system provides three pre-configured dashboards:

- **Code Quality Dashboard**: Bug tracking, test failures, code review issues
- **Pattern Analysis Dashboard**: Pattern frequency, effectiveness, trends
- **Development Trends Dashboard**: AI code generation metrics, deployment issues

## Why Superset?

Apache Superset offers several advantages for feedback-loop metrics:

### Key Benefits

✅ **Open Source**: Apache 2.0 license (compatible with feedback-loop's MIT license)  
✅ **Powerful Visualizations**: 40+ chart types, interactive dashboards  
✅ **SQL Support**: Native SQL Lab for custom queries  
✅ **Real-time Updates**: Configurable refresh rates  
✅ **Multi-user**: Team collaboration features  
✅ **Extensible**: Custom visualization plugins  
✅ **Production Ready**: Used by Airbnb, Twitter, Netflix  

### Use Cases

1. **Development Team Analytics**
   - Track code quality trends
   - Monitor pattern effectiveness
   - Identify recurring issues

2. **Management Reporting**
   - KPI dashboards
   - Sprint retrospectives
   - Quality metrics over time

3. **Continuous Improvement**
   - A/B testing pattern changes
   - Measuring AI assistance impact
   - ROI tracking for pattern library

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Feedback Loop System                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────┐       ┌──────────────┐                     │
│  │   Tests    │──────>│   Metrics    │                     │
│  │  (pytest)  │       │  Collector   │                     │
│  └────────────┘       └──────┬───────┘                     │
│                              │                              │
│                              v                              │
│                     ┌─────────────────┐                    │
│                     │ metrics_data.json│                    │
│                     └────────┬─────────┘                    │
│                              │                              │
└──────────────────────────────┼──────────────────────────────┘
                               │
                               │ export_to_db.py
                               v
┌─────────────────────────────────────────────────────────────┐
│                      SQL Database                            │
│                 (SQLite or PostgreSQL)                       │
├─────────────────────────────────────────────────────────────┤
│  • metrics_bugs             • metrics_deployment             │
│  • metrics_test_failures    • metrics_code_generation        │
│  • metrics_code_reviews     • pattern_effectiveness          │
│  • metrics_performance      • metrics_summary                │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               │ SQL queries
                               v
┌─────────────────────────────────────────────────────────────┐
│                    Apache Superset                           │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────┐   │
│  │  Code Quality │  │    Pattern    │  │  Development │   │
│  │   Dashboard   │  │    Analysis   │  │    Trends    │   │
│  └───────────────┘  └───────────────┘  └──────────────┘   │
│                                                              │
│  • Interactive charts    • SQL Lab      • Alerts            │
│  • Filters              • Exports       • Sharing           │
└─────────────────────────────────────────────────────────────┘
```

## Setup Guide

### Prerequisites

- Python 3.8+
- feedback-loop installed
- Docker (recommended for Superset) or manual Superset installation

### Step 1: Install Dependencies

```bash
# Install database dependencies
pip install sqlalchemy psycopg2-binary
```

### Step 2: Choose Database Backend

**Option A: SQLite (Development)**
```bash
# No additional setup needed
# Database will be created automatically
```

**Option B: PostgreSQL (Production)**
```bash
# Using Docker
docker run -d \
  --name feedback-postgres \
  -e POSTGRES_DB=feedback_loop \
  -e POSTGRES_USER=feedback_user \
  -e POSTGRES_PASSWORD=secure_password \
  -p 5432:5432 \
  postgres:14

# Or install PostgreSQL locally
# See database/connection_examples.md for details
```

### Step 3: Install Apache Superset

**Option A: Docker (Recommended)**
```bash
# Clone official Apache Superset
git clone https://github.com/apache/superset.git
cd superset

# Start Superset
docker-compose -f docker-compose-non-dev.yml up -d

# Access at http://localhost:8088
# Default credentials: admin/admin
```

**Note:** If you need custom modifications, you can use a fork (e.g., `https://github.com/doronpers/superset`), but for most use cases, the official Apache Superset repository is recommended.

**Option B: Manual Installation**
```bash
pip install apache-superset
superset db upgrade
superset fab create-admin
superset init
superset run -h 0.0.0.0 -p 8088
```

### Step 4: Collect Metrics

```bash
# Run tests with metrics collection
cd /path/to/your/project
pytest --enable-metrics

# Or collect metrics manually
python -c "
from metrics.collector import MetricsCollector
collector = MetricsCollector()
# ... add metrics ...
with open('metrics_data.json', 'w') as f:
    f.write(collector.export_json())
"
```

### Step 5: Export Metrics to Database

```bash
# For SQLite (development)
python superset-dashboards/scripts/export_to_db.py --format sqlite

# For PostgreSQL (production)
export DB_URI="postgresql://feedback_user:secure_password@localhost:5432/feedback_loop"
python superset-dashboards/scripts/export_to_db.py --format postgresql --db-uri "$DB_URI"
```

### Step 6: Configure Superset Database Connection

1. Open Superset: http://localhost:8088
2. Log in (admin/admin)
3. Navigate to: **Data** → **Databases** → **+ Database**
4. Fill in connection details:

**For SQLite:**
```
Database: Feedback Loop Metrics
SQLAlchemy URI: sqlite:////absolute/path/to/feedback-loop/metrics.db
```

**For PostgreSQL:**
```
Database: Feedback Loop Metrics
SQLAlchemy URI: postgresql://feedback_user:secure_password@localhost:5432/feedback_loop
```

5. Click **Test Connection**
6. Click **Connect**

### Step 7: Add Datasets

1. Navigate to: **Data** → **Datasets** → **+ Dataset**
2. Select database: "Feedback Loop Metrics"
3. Add each table:
   - metrics_bugs
   - metrics_test_failures
   - metrics_code_reviews
   - metrics_performance
   - metrics_deployment
   - metrics_code_generation
   - pattern_effectiveness
   - metrics_summary

### Step 8: Create Dashboards

You can either:

**Option A: Create dashboards manually**
- Use the Superset UI to create charts and dashboards
- Follow the examples in `superset-dashboards/dashboards/`

**Option B: Import pre-configured dashboards** (if export/import is available in your Superset version)
```bash
# Import dashboard configurations
# (Note: This requires Superset CLI or API access)
```

## Dashboard Workflows

### Daily Development Workflow

```bash
# 1. Write code and tests
vim my_module.py

# 2. Run tests with metrics
pytest --enable-metrics

# 3. Sync to database
python superset-dashboards/scripts/sync_metrics.py

# 4. View dashboards
# Open http://localhost:8088
```

### CI/CD Integration

Add to `.github/workflows/metrics.yml`:

```yaml
name: Metrics Collection

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  collect-metrics:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -e .[test]
          pip install sqlalchemy psycopg2-binary
      
      - name: Run tests with metrics
        run: pytest --enable-metrics
      
      - name: Export to database
        env:
          DB_URI: ${{ secrets.METRICS_DB_URI }}
        run: |
          python superset-dashboards/scripts/export_to_db.py \
            --format postgresql \
            --db-uri "$DB_URI"
```

### Automated Sync

Set up cron job for periodic sync:

```bash
# Edit crontab
crontab -e

# Add entry (sync every hour)
0 * * * * cd /path/to/feedback-loop && /usr/bin/python3 superset-dashboards/scripts/sync_metrics.py >> /var/log/metrics-sync.log 2>&1
```

## Advanced Usage

### Custom Queries in SQL Lab

Navigate to **SQL** → **SQL Lab** in Superset and run custom queries:

```sql
-- Top 10 patterns by bug count
SELECT pattern, COUNT(*) as bug_count
FROM metrics_bugs
WHERE timestamp > NOW() - INTERVAL '30 days'
GROUP BY pattern
ORDER BY bug_count DESC
LIMIT 10;

-- Pattern effectiveness over time
SELECT 
    DATE_TRUNC('week', period_start) as week,
    pattern_name,
    AVG(effectiveness_score) as avg_effectiveness
FROM pattern_effectiveness
GROUP BY week, pattern_name
ORDER BY week DESC, avg_effectiveness DESC;

-- Code generation success rate by confidence
SELECT 
    ROUND(confidence, 1) as confidence_bucket,
    COUNT(*) as total,
    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successes,
    ROUND(100.0 * SUM(CASE WHEN success THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
FROM metrics_code_generation
GROUP BY confidence_bucket
ORDER BY confidence_bucket;
```

### Creating Custom Charts

1. Navigate to **Charts** → **+ Chart**
2. Select dataset (e.g., metrics_bugs)
3. Choose visualization type
4. Configure metrics and dimensions
5. Apply filters
6. Save to dashboard

### Setting Up Alerts

1. Create a chart
2. Click **⋮** → **Set up Alerts**
3. Configure alert conditions
4. Set notification channels (email, Slack, etc.)
5. Save alert

### Exporting Data

From any dashboard or chart:
- **CSV**: Click **⋮** → **Download as CSV**
- **JSON**: Click **⋮** → **Download as JSON**
- **Image**: Click **⋮** → **Download as Image**

## Best Practices

### Database Management

1. **Regular Backups**
   ```bash
   # PostgreSQL
   pg_dump feedback_loop > backup_$(date +%Y%m%d).sql
   
   # SQLite
   cp metrics.db metrics_backup_$(date +%Y%m%d).db
   ```

2. **Index Optimization**
   ```sql
   -- Add indexes for common queries
   CREATE INDEX idx_bugs_pattern_timestamp ON metrics_bugs(pattern, timestamp);
   CREATE INDEX idx_generation_success ON metrics_code_generation(success, timestamp);
   ```

3. **Data Retention**
   ```sql
   -- Archive old data (older than 1 year)
   DELETE FROM metrics_bugs WHERE timestamp < NOW() - INTERVAL '1 year';
   ```

### Dashboard Design

1. **Start Simple**: Begin with key metrics, add complexity as needed
2. **Use Filters**: Add dashboard-level filters for time range, pattern, etc.
3. **Color Coding**: Use consistent colors (red=bad, green=good)
4. **Refresh Rates**: Set appropriate refresh intervals (5-15 minutes typical)
5. **Mobile Friendly**: Test dashboards on mobile devices

### Performance Optimization

1. **Materialized Views** (PostgreSQL)
   ```sql
   CREATE MATERIALIZED VIEW pattern_summary AS
   SELECT 
       pattern,
       COUNT(*) as total_bugs,
       MAX(timestamp) as last_occurrence
   FROM metrics_bugs
   GROUP BY pattern;
   
   -- Refresh periodically
   REFRESH MATERIALIZED VIEW pattern_summary;
   ```

2. **Query Caching**: Enable in Superset config
3. **Async Queries**: For long-running queries

## Troubleshooting

### Common Issues

**Problem**: "Cannot connect to database"

**Solution**:
- Verify database is running
- Check connection URI
- Test connection with psql or sqlite3
- Check firewall rules

---

**Problem**: "No data in dashboards"

**Solution**:
```bash
# Verify metrics were collected
cat metrics_data.json

# Re-run export
python superset-dashboards/scripts/export_to_db.py --format sqlite

# Check database has data
sqlite3 metrics.db "SELECT COUNT(*) FROM metrics_bugs;"
```

---

**Problem**: "Dashboard not loading"

**Solution**:
- Check Superset logs: `docker logs superset_app`
- Verify dataset is properly configured
- Refresh browser cache (Ctrl+Shift+R)

---

**Problem**: "Slow dashboard performance"

**Solution**:
- Add database indexes
- Reduce time range filter
- Enable query caching
- Consider materialized views

## Additional Resources

- [Apache Superset Documentation](https://superset.apache.org/docs/intro)
- [Superset GitHub](https://github.com/apache/superset)
- [feedback-loop Documentation](../docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

## License & Attribution

Apache Superset is licensed under Apache License 2.0.

**Required Attribution:**
When distributing or modifying, include:
- Apache License 2.0 notice
- Acknowledgment of Apache Superset use

This integration code is licensed under MIT (same as feedback-loop).

## Support

For issues or questions:
- feedback-loop: https://github.com/doronpers/feedback-loop/issues
- Apache Superset: https://github.com/apache/superset/issues
