# UATMMS Quick Start: Credentials & Setup

Fast-track guide for getting all credentials and dependencies in place.

## 5-Minute Essentials

### 1. Firebase
```bash
# 1. Go to https://console.firebase.google.com
# 2. Create project or use existing
# 3. Get Service Account JSON:
#    - Settings → Service Accounts → Generate New Private Key
# 4. Set environment variable:

export FIREBASE_CREDENTIALS_JSON=$(cat serviceAccountKey.json | jq -c .)
# Or on Windows:
# $env:FIREBASE_CREDENTIALS_JSON = Get-Content serviceAccountKey.json -Raw
```

### 2. PostgreSQL
```bash
# Docker (easiest):
docker run --name uatmms-db \
  -e POSTGRES_USER=uatmms_user \
  -e POSTGRES_PASSWORD=uatmms_pass \
  -e POSTGRES_DB=uatmms_db \
  -p 5432:5432 \
  -d postgres:16

# Test connection:
psql postgresql://uatmms_user:uatmms_pass@localhost:5432/uatmms_db -c "SELECT 1"
```

### 3. Redis
```bash
# Docker (easiest):
docker run --name uatmms-redis \
  -p 6379:6379 \
  -d redis:7-alpine

# Test connection:
redis-cli ping  # Should return PONG
```

### 4. AWS S3 (optional, for model storage)
```bash
# Prerequisites:
# 1. AWS Account: https://aws.amazon.com
# 2. Create S3 bucket: uatmms-models
# 3. Create IAM user with S3 access
# 4. Generate Access Keys

export AWS_ACCESS_KEY_ID="your-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_REGION="us-east-1"
export S3_BUCKET="uatmms-models"
```

### 5. SUMO Simulation
```bash
# Install:
# Windows: Download from https://sumo.dlr.de/download
# macOS: brew install sumo
# Linux: apt-get install sumo

# Verify:
sumo --version

# Set environment:
export SUMO_HOME="/opt/sumo"  # or C:\Program Files\SUMO
export SUMO_BINARY="/opt/sumo/bin/sumo"
```

### 6. Python Dependencies
```bash
# Install all requirements:
pip install -r backend/requirements.txt

# Install additional packages if needed:
pip install firebase-admin psycopg2-binary pytest-asyncio

# Verify key packages:
python -c "import firebase_admin; import sqlalchemy; import torch; print('All OK')"
```

---

## Create `.env` File

```bash
# Copy template
cp .env.example .env

# Edit with your values (nano, code, vim, etc.)
code .env
```

**Minimum required values**:
```bash
# Firebase
FIREBASE_CREDENTIALS_JSON='{"type":"service_account",...}'

# Database
DATABASE_URL="postgresql://uatmms_user:uatmms_pass@localhost:5432/uatmms_db"

# Redis
REDIS_URL="redis://localhost:6379/0"

# App
APP_ENV="development"
SECRET_KEY="your-secret-key-change-in-production"
```

---

## Credentials Needed Per Component

| Component | Type | Required | Dev/Prod | How to Get |
|-----------|------|----------|----------|-----------|
| Firebase | JSON Key | ✅ | Both | Console → Service Accounts |
| PostgreSQL | Password | ✅ | Both | Create DB user |
| Redis | Connection String | ✅ | Both | Docker or cloud |
| AWS S3 | Access Keys | ❌ | Prod | AWS IAM |
| SUMO | Binary Path | ✅ | Both | Download/Install |
| PyTorch | - | ✅ | Both | `pip install` |
| Docker | - | ❌ | Both | Optional |
| Git | SSH Key | ❌ | - | `ssh-keygen` |

---

## Verification Script

```bash
#!/bin/bash
# verify_setup.sh - Check all credentials are in place

echo "🔍 Checking UATMMS Setup..."

# Firebase
if [[ -z "$FIREBASE_CREDENTIALS_JSON" ]]; then
  echo "❌ FIREBASE_CREDENTIALS_JSON not set"
else
  echo "✅ Firebase credentials found"
fi

# PostgreSQL
if ! psql "$DATABASE_URL" -c "SELECT 1" > /dev/null 2>&1; then
  echo "❌ PostgreSQL connection failed"
else
  echo "✅ PostgreSQL connected"
fi

# Redis
if ! redis-cli -u "$REDIS_URL" ping > /dev/null 2>&1; then
  echo "❌ Redis connection failed"
else
  echo "✅ Redis connected"
fi

# SUMO
if ! command -v sumo &> /dev/null; then
  echo "❌ SUMO not found in PATH"
else
  echo "✅ SUMO installed: $(sumo --version)"
fi

# Python
if ! python -c "import firebase_admin, sqlalchemy, torch" 2>/dev/null; then
  echo "❌ Required Python packages missing"
else
  echo "✅ Python packages OK"
fi

echo "🎉 Setup verification complete!"
```

Run it:
```bash
chmod +x verify_setup.sh
./verify_setup.sh
```

---

## Common Issues & Fixes

### "ModuleNotFoundError: No module named 'firebase_admin'"
```bash
pip install firebase-admin
```

### "Error: could not connect to server: Connection refused"
```bash
# PostgreSQL not running
docker ps | grep postgres  # If not listed, restart:
docker start uatmms-db
```

### "Access Denied: FIREBASE_CREDENTIALS_JSON"
```bash
# Check JSON format:
echo $FIREBASE_CREDENTIALS_JSON | jq .  # Should be valid JSON

# Or use file path:
export FIREBASE_CREDENTIALS_FILE="/path/to/serviceAccountKey.json"
```

### "Exec format error: SUMO_BINARY"
```bash
# Path may be incorrect
which sumo  # Find correct path
export SUMO_BINARY="$(which sumo)"
```

---

## Step-by-Step Initialization

```bash
# 1. Clone repository
git clone <your-repo>
cd UATMMS/UATMMS

# 2. Create Python virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Start Docker services
docker-compose up -d  # Requires docker-compose.yml

# 5. Create .env file with credentials
cp .env.example .env
# Edit .env with your credentials

# 6. Run database migrations
cd backend
alembic upgrade head
python -c "from app.auth.rbac import init_rbac; from app.db.session import SessionLocal; db = SessionLocal(); init_rbac(db)"

# 7. Verify setup
python scripts/verify_setup.py

# 8. Run tests
pytest backend/tests/ -v

# 9. Start backend server
uvicorn app.main:app --reload --port 8000
```

---

## Docker Compose Quick Start

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: uatmms_user
      POSTGRES_PASSWORD: uatmms_pass
      POSTGRES_DB: uatmms_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

Then:
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f postgres

# Stop all
docker-compose down
```

---

## Production Credentials Strategy

| Component | Development | Production |
|-----------|-------------|------------|
| Firebase | Test project | Production project |
| DB | Local Docker | AWS RDS / Cloud SQL |
| Redis | Local Docker | AWS ElastiCache / Cloud Memorystore |
| S3 | LocalStack | AWS S3 |
| Credentials | `.env` file | AWS Secrets Manager / Azure Key Vault |
| Secrets | Plaintext OK | Encrypted, rotated |
| Backups | Optional | Daily, tested |

---

## Checklist Before Starting Development

- [ ] `git clone` repository
- [ ] Python 3.10+ installed
- [ ] Docker installed (optional but recommended)
- [ ] Firebase service account JSON downloaded
- [ ] PostgreSQL running (Docker or local)
- [ ] Redis running (Docker or local)
- [ ] SUMO installed and in PATH
- [ ] `.env` file created with all credentials
- [ ] `pip install -r requirements.txt` successful
- [ ] Database migrations applied: `alembic upgrade head`
- [ ] RBAC initialized: `python -c "from app.auth.rbac import init_rbac..."`
- [ ] Tests pass: `pytest backend/tests/ -v`
- [ ] Backend starts: `uvicorn app.main:app --reload`

---

## Need Help?

1. **Firebase Issues**: https://firebase.google.com/support
2. **Database Issues**: https://www.postgresql.org/community
3. **SUMO Issues**: https://sumo.dlr.de/wiki/Contact
4. **AWS Issues**: https://aws.amazon.com/support
5. **Project Issues**: Check `docs/CREDENTIALS_AND_SETUP.md` for detailed setup

---

Last Updated: October 2026
