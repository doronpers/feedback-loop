# Apache Superset Dashboard Integration

This directory contains Apache Superset dashboard configurations and integration scripts for visualizing feedback-loop metrics.

## 📚 Documentation Index

**Start Here:**

- **[SUPERSET_ANALYSIS_SUMMARY.md](SUPERSET_ANALYSIS_SUMMARY.md)** - Executive summary and quick start guide
- **[DASHBOARD_DESIGN_RECOMMENDATIONS.md](DASHBOARD_DESIGN_RECOMMENDATIONS.md)** - Detailed dashboard designs with SQL queries
- **[DATABASE_CONFIGURATION.md](DATABASE_CONFIGURATION.md)** - Complete database schema and connection guide

**Also See:**

- **[SUPERSET_INTEGRATION.md](../Documentation/SUPERSET_INTEGRATION.md)** - General integration guide

## Overview

Apache Superset is used to provide powerful analytics and visualization capabilities for:

- **Code Quality Metrics**: Track complexity, coverage, and lint scores over time
- **Pattern Analysis**: Visualize pattern frequency and effectiveness
- **Development Trends**: Monitor AI-assisted development metrics and improvement patterns
- **Fusion Engine Analytics**: Monitor AI code generation with pattern fusion
- **Confidence Scoring**: Track pattern effectiveness and calibration
- **Detection Results**: Comprehensive bug, test, and review issue tracking
- **Audit Reporting**: Compliance and pattern analysis reporting

## Directory Structure

```
superset-dashboards/
├── README.md                    # This file
├── dashboards/                  # Dashboard JSON exports from Superset
│   ├── code_quality_dashboard.json
│   ├── pattern_analysis_dashboard.json
│   └── development_trends_dashboard.json
├── database/                    # Database configuration and models
│   ├── models.py               # SQLAlchemy models for metrics
│   └── connection_examples.py  # Example database configurations
└── scripts/                     # Integration scripts
    ├── export_to_db.py         # Export metrics to database
    ├── import_dashboards.py    # Import dashboard configs to Superset
    └── sync_metrics.py         # Automated sync script
```

## Prerequisites

### 1. Install Apache Superset

For local development with Docker:

```bash
git clone https://github.com/apache/superset.git
cd superset
docker-compose -f docker-compose-non-dev.yml up
```

Or use your fork:

```bash
git clone https://github.com/doronpers/superset.git
cd superset
docker-compose -f docker-compose-non-dev.yml up
```

Access Superset at: <http://localhost:8088>

- Default credentials: admin/admin

### 2. Install Additional Python Dependencies

```bash
pip install sqlalchemy psycopg2-binary
```

## Quick Start

### Step 1: Export Metrics to Database

Export your collected metrics to a SQLite database (for development):

```bash
python superset-dashboards/scripts/export_to_db.py --format sqlite
```

Or to PostgreSQL (for production):

```bash
export DB_URI="postgresql://user:password@localhost:5432/feedback_loop"
python superset-dashboards/scripts/export_to_db.py --format postgresql --db-uri "$DB_URI"
```

### Step 2: Configure Superset Database Connection

1. Log into Superset (<http://localhost:8088>)
2. Go to **Data** → **Databases** → **+ Database**
3. Choose your database type (SQLite or PostgreSQL)
4. Configure connection:

**For SQLite:**

```
SQLAlchemy URI: sqlite:////path/to/feedback-loop/metrics.db
```

**For PostgreSQL:**

```
SQLAlchemy URI: postgresql://user:password@localhost:5432/feedback_loop
```

### Step 3: Import Pre-configured Dashboards

```bash
python superset-dashboards/scripts/import_dashboards.py
```

This will import the following dashboards:

- **Code Quality Dashboard**: Visualizes bugs, test failures, and code review issues
- **Pattern Analysis Dashboard**: Shows pattern frequency and effectiveness
- **Development Trends Dashboard**: Tracks development metrics over time

### Step 4: Set Up Automated Sync (Optional)

For continuous dashboard updates, set up a cron job or scheduled task:

```bash
# Run sync every hour
0 * * * * cd /path/to/feedback-loop && python superset-dashboards/scripts/sync_metrics.py
```

## Dashboard Descriptions

### Code Quality Dashboard

Visualizes:

- **Bug Trends**: Line chart showing bug counts by pattern over time
- **Test Failure Analysis**: Bar chart of test failures by pattern
- **Code Review Issues**: Severity breakdown (high, medium, low)
- **Top Problem Patterns**: Table showing most frequent issues

**Key Metrics:**

- Total bugs by pattern
- Test failure rate
- Code review issue distribution
- Pattern violation frequency

### Pattern Analysis Dashboard

Visualizes:

- **Pattern Effectiveness**: Heatmap showing pattern success rates
- **Pattern Frequency**: Bar chart of pattern usage
- **New vs Known Patterns**: Pie chart showing pattern discovery
- **Pattern Lifecycle**: Timeline showing pattern adoption

**Key Metrics:**

- Pattern application count
- Pattern effectiveness score
- Pattern discovery rate
- Time to pattern adoption

### Development Trends Dashboard

Visualizes:

- **AI-Assisted Development**: Line chart showing generation success rate
- **Code Generation Metrics**: Bar chart of patterns applied per generation
- **Deployment Issues**: Timeline of production issues
- **Performance Metrics**: Scatter plot of execution time vs file size

**Key Metrics:**

- Code generation success rate
- Average patterns applied per generation
- Deployment issue frequency
- Performance bottleneck identification

## Database Schema

The metrics are exported to the following tables:

- `metrics_bugs`: Bug occurrences with pattern, error, code snippet, file path
- `metrics_test_failures`: Test failure records
- `metrics_code_reviews`: Code review issues
- `metrics_performance`: Performance metrics (memory, execution time)
- `metrics_deployment`: Deployment issues
- `metrics_code_generation`: Code generation events

See `database/models.py` for detailed schema definitions.

## Workflow Integration

### CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/metrics.yml
- name: Collect Metrics
  run: pytest --enable-metrics

- name: Export to Database
  run: python superset-dashboards/scripts/export_to_db.py --format postgresql
  env:
    DB_URI: ${{ secrets.METRICS_DB_URI }}
```

### Local Development Workflow

```bash
# 1. Run tests with metrics collection
pytest --enable-metrics

# 2. Analyze metrics
feedback-loop analyze

# 3. Export to database
python superset-dashboards/scripts/export_to_db.py --format sqlite

# 4. View dashboards in Superset
# Open http://localhost:8088 in browser
```

## Compliance & Attribution

Apache Superset is licensed under Apache License 2.0, which is compatible with this project's MIT license.

**Required Attribution:**

- Include Apache License 2.0 notice when distributing
- Acknowledge use of Apache Superset in documentation

See [LICENSE](../LICENSE) for more details.

## Troubleshooting

### Database Connection Issues

**Problem**: Cannot connect to database from Superset
**Solution**:

- Verify database is running
- Check SQLAlchemy URI format
- Ensure database user has required permissions

### Dashboard Import Fails

**Problem**: Dashboard import returns errors
**Solution**:

- Ensure database connection is configured first
- Verify all required tables exist
- Check Superset version compatibility

### No Data in Dashboards

**Problem**: Dashboards show no data
**Solution**:

- Run `export_to_db.py` to populate database
- Verify metrics were collected (check metrics_data.json)
- Refresh dashboard in Superset

## Advanced Usage

### Custom Dashboards

Create custom dashboards in Superset UI and export them:

1. Create dashboard in Superset
2. Export dashboard: **Settings** → **Export**
3. Save JSON to `dashboards/` directory
4. Document dashboard in this README

### PostgreSQL Performance Optimization

For large datasets, add indexes:

```sql
CREATE INDEX idx_bugs_pattern ON metrics_bugs(pattern, timestamp);
CREATE INDEX idx_generation_timestamp ON metrics_code_generation(timestamp);
CREATE INDEX idx_test_failures_pattern ON metrics_test_failures(pattern_violated);
```

### Multi-Repository Setup

To aggregate metrics from multiple repositories:

1. Use same PostgreSQL database for all repos
2. Add `repository` column to track source
3. Create cross-repository dashboard views

## Support

For issues or questions:

- feedback-loop issues: <https://github.com/doronpers/feedback-loop/issues>
- Apache Superset docs: <https://superset.apache.org/docs/intro>
- Superset issues: <https://github.com/apache/superset/issues>

## License

This integration code is licensed under MIT (same as feedback-loop).
Apache Superset is licensed under Apache License 2.0.
