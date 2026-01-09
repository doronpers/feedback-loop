# Example Superset Database Connection Configurations

## SQLite (Local Development)

```python
from sqlalchemy import create_engine

# Basic SQLite connection
db_path = '/path/to/feedback-loop/metrics.db'
engine = create_engine(f'sqlite:///{db_path}')
```

**Superset SQLAlchemy URI:**
```
sqlite:////absolute/path/to/feedback-loop/metrics.db
```

**Pros:**
- No installation required
- Perfect for local development
- Easy to backup (single file)
- No configuration needed

**Cons:**
- Not suitable for concurrent access
- Limited query performance for large datasets
- Not recommended for production

---

## PostgreSQL (Production)

```python
from sqlalchemy import create_engine

# PostgreSQL connection
db_uri = 'postgresql://username:password@localhost:5432/feedback_loop'
engine = create_engine(db_uri)
```

**Superset SQLAlchemy URI:**
```
postgresql://username:password@localhost:5432/feedback_loop
```

**Setup PostgreSQL Database:**
```sql
-- Create database
CREATE DATABASE feedback_loop;

-- Create user
CREATE USER feedback_user WITH PASSWORD 'secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE feedback_loop TO feedback_user;
```

**Pros:**
- Excellent for production use
- Supports concurrent access
- Advanced query optimization
- ACID compliance
- Rich analytics features

**Cons:**
- Requires PostgreSQL installation
- More complex setup
- Requires server management

---

## PostgreSQL with SSL (Production - Secure)

```python
from sqlalchemy import create_engine

# PostgreSQL with SSL
db_uri = (
    'postgresql://username:password@hostname:5432/feedback_loop'
    '?sslmode=require'
)
engine = create_engine(db_uri)
```

**Superset SQLAlchemy URI:**
```
postgresql://username:password@hostname:5432/feedback_loop?sslmode=require
```

---

## Environment-Based Configuration

**Development:**
```bash
export METRICS_DB_URI="sqlite:////home/user/feedback-loop/metrics.db"
```

**Staging:**
```bash
export METRICS_DB_URI="postgresql://user:pass@staging-db:5432/feedback_loop_staging"
```

**Production:**
```bash
export METRICS_DB_URI="postgresql://user:pass@prod-db:5432/feedback_loop?sslmode=require"
```

---

## Cloud Database Services

### AWS RDS (PostgreSQL)

```
postgresql://username:password@mydb.abc123.us-west-2.rds.amazonaws.com:5432/feedback_loop
```

### Google Cloud SQL (PostgreSQL)

```
postgresql://username:password@/feedback_loop?host=/cloudsql/project:region:instance
```

### Azure Database for PostgreSQL

```
postgresql://username@servername:password@servername.postgres.database.azure.com:5432/feedback_loop?sslmode=require
```

### Heroku Postgres

```
postgres://username:password@hostname:5432/database_name
```

---

## Connection Pooling (Recommended for Production)

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'postgresql://user:pass@host:5432/feedback_loop',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True  # Verify connections before use
)
```

---

## Docker Compose Example

Create a `docker-compose.yml` for local PostgreSQL:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: feedback_loop
      POSTGRES_USER: feedback_user
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Start with:
```bash
docker-compose up -d
```

Connection URI:
```
postgresql://feedback_user:dev_password@localhost:5432/feedback_loop
```

---

## Security Best Practices

1. **Never commit credentials**
   - Use environment variables
   - Use secret management services (AWS Secrets Manager, HashiCorp Vault)

2. **Use strong passwords**
   - Minimum 16 characters
   - Mix of letters, numbers, symbols

3. **Enable SSL/TLS**
   - Always use `sslmode=require` in production
   - Use certificate verification when possible

4. **Limit database permissions**
   - Create separate users for different purposes
   - Grant only necessary permissions

5. **Network security**
   - Use VPC/private networks in cloud
   - Configure firewall rules
   - Use bastion hosts for access

---

## Testing Connection

```python
# test_connection.py
from sqlalchemy import create_engine, text

def test_connection(db_uri):
    try:
        engine = create_engine(db_uri)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✓ Database connection successful!")
            return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

# Test
db_uri = "your_database_uri_here"
test_connection(db_uri)
```

---

## Troubleshooting

### Cannot connect to PostgreSQL

**Error:** `could not connect to server`

**Solutions:**
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify port is correct (default: 5432)
- Check firewall rules
- Verify host/IP address is correct

### Authentication failed

**Error:** `password authentication failed`

**Solutions:**
- Verify username and password
- Check `pg_hba.conf` for authentication method
- Ensure user has login privilege

### Database does not exist

**Error:** `database "feedback_loop" does not exist`

**Solutions:**
- Create database: `CREATE DATABASE feedback_loop;`
- Check database name spelling

### SSL connection error

**Error:** `SSL connection error`

**Solutions:**
- Add `?sslmode=disable` for local development
- For production, configure SSL certificates properly
- Use `sslmode=require` with valid certificates
