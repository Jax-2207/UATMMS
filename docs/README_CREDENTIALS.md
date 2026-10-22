# UATMMS Credentials & Configuration - README

**Start here for complete information on all credentials and configuration needed to run UATMMS.**

---

## 📚 Documentation Files

This guide is split across multiple files for easy navigation:

1. **This File** (`README_CREDENTIALS.md`)
   - Overview and quick links
   - Which file to read for your needs

2. **[SETUP_QUICK_START.md](../SETUP_QUICK_START.md)** ⭐ **START HERE**
   - 5-minute quick start
   - Docker commands
   - Step-by-step initialization
   - Common troubleshooting

3. **[CREDENTIALS_AND_SETUP.md](./CREDENTIALS_AND_SETUP.md)** 📖 **DETAILED GUIDE**
   - Comprehensive credential requirements
   - Detailed setup instructions per service
   - Development vs Production
   - Security best practices
   - Full troubleshooting guide

4. **[CREDENTIALS_MATRIX.md](./CREDENTIALS_MATRIX.md)** 🔍 **QUICK REFERENCE**
   - Summary table of all credentials
   - Exact format and examples
   - Sensitivity levels
   - Rotation schedule

5. **[.env.example](../.env.example)** 🔑 **TEMPLATE**
   - All configuration options in one file
   - Copy to `.env` and fill in your values
   - Comments explain each field

---

## 🚀 Quick Start (3 Steps)

### 1. Set Up Services (10 minutes)
```bash
# Start PostgreSQL and Redis with Docker
docker run --name uatmms-db \
  -e POSTGRES_USER=uatmms_user \
  -e POSTGRES_PASSWORD=uatmms_pass \
  -e POSTGRES_DB=uatmms_db \
  -p 5432:5432 \
  -d postgres:16

docker run --name uatmms-redis \
  -p 6379:6379 \
  -d redis:7-alpine
```

### 2. Create `.env` File (5 minutes)
```bash
# Copy template
cp .env.example .env

# Edit with your credentials
# Minimum required:
# - FIREBASE_CREDENTIALS_JSON
# - DATABASE_URL
# - REDIS_URL
```

### 3. Verify Setup
```bash
# Run verification
python scripts/verify_setup.py

# Or manually:
psql $DATABASE_URL -c "SELECT 1"
redis-cli -u $REDIS_URL ping
echo $FIREBASE_CREDENTIALS_JSON | python -m json.tool
```

---

## 📋 What Credentials Do I Need?

### **Minimum (Development)**
| Service | Credential | Required |
|---------|-----------|----------|
| PostgreSQL | Connection String | ✅ |
| Redis | URL | ✅ |
| Firebase | Service Account JSON | ✅ |
| SUMO | Binary Path | ✅ |
| Python | Installed (3.10+) | ✅ |

### **Recommended (Full Development)**
All above plus:
- AWS S3 (if training RL models)
- Docker (for container setup)
- Git (for version control)

### **Required (Production)**
All above plus:
- SSL/TLS Certificates
- AWS KMS (for secrets encryption)
- CloudWatch/Monitoring
- Backup solution
- Separate prod credentials for each service

---

## 🔑 Where to Get Each Credential

### Firebase
**Get from**: https://console.firebase.google.com
- Create project
- Service Accounts → Generate Key
- Download JSON

### PostgreSQL
**Get from**: Create locally or use cloud provider
- Local: `docker run postgres:16`
- Cloud: AWS RDS, Azure Database, Google Cloud SQL

### Redis
**Get from**: Create locally or use cloud provider
- Local: `docker run redis:7-alpine`
- Cloud: AWS ElastiCache, Azure Cache

### AWS S3
**Get from**: https://aws.amazon.com
- Create bucket
- IAM → Create user
- Generate access keys

### SUMO
**Get from**: https://sumo.dlr.de/wiki/Downloads
- Download installer
- Or: `brew install sumo` / `apt-get install sumo`

### Network Files
**Get from**: Choose one:
- OpenStreetMap (https://www.openstreetmap.org)
- SUMO sample networks
- Your own topology

---

## 📊 Credentials by Phase

### Phases 1-3: Core (Network & Traffic)
```
SUMO_HOME, SUMO_BINARY, Network File, Route File
```
⏱️ ~10 minutes to set up

### Phases 4-5: Safety & Incidents
```
+ DATABASE_URL (PostgreSQL)
```
⏱️ +5 minutes

### Phase 6: Prediction
```
+ Scikit-learn, XGBoost (pip install)
```
⏱️ +5 minutes

### Phase 7: RL & ML
```
+ PYTORCH_CUDA_ALLOC_CONF, AWS S3 Credentials
+ Stable Baselines3 (pip install)
```
⏱️ +30 minutes (GPU setup optional)

### Phase 8: Database & Auth ⭐ **CRITICAL**
```
+ FIREBASE_CREDENTIALS_JSON
+ REDIS_URL
+ SECRET_KEY, JWT_SECRET_KEY
```
⏱️ +15 minutes

### Phase 9: Dashboard
```
+ WEBSOCKET settings
+ Redis (already have from Phase 8)
```
⏱️ +5 minutes

### Phase 10: 3D Twin
```
+ TWIN settings
+ Unity/3D engine (separate from backend)
```
⏱️ +20 minutes

---

## 🔐 Security Checklist

Before starting development:
- [ ] `.env` is in `.gitignore`
- [ ] No credentials in code
- [ ] Firebase JSON file not committed
- [ ] AWS keys not in repository
- [ ] Database password is strong (16+ chars)
- [ ] Redis password set (if production)

Before production:
- [ ] All credentials in Secrets Manager
- [ ] Keys rotated recently
- [ ] Separate dev/staging/prod credentials
- [ ] SSL/TLS enabled
- [ ] Database backups tested
- [ ] Monitoring alerts configured
- [ ] Access logs enabled

---

## 🚨 Common Issues

**"Firebase credentials not found"**
```bash
# Fix: Set FIREBASE_CREDENTIALS_JSON or FIREBASE_CREDENTIALS_FILE
export FIREBASE_CREDENTIALS_JSON='{"type":"service_account",...}'
# Or
export FIREBASE_CREDENTIALS_FILE="/path/to/serviceAccountKey.json"
```

**"Cannot connect to PostgreSQL"**
```bash
# Fix: Verify database is running and accessible
psql postgresql://user:pass@host:port/dbname -c "SELECT 1"
```

**"SUMO not found"**
```bash
# Fix: Verify installation and set path
which sumo  # Find the path
export SUMO_BINARY="/full/path/to/sumo"
```

**"Invalid JSON in Firebase credentials"**
```bash
# Fix: Validate JSON syntax
echo $FIREBASE_CREDENTIALS_JSON | python -m json.tool
```

See [CREDENTIALS_AND_SETUP.md](./CREDENTIALS_AND_SETUP.md#troubleshooting) for more troubleshooting.

---

## 📖 Reading Guide

**I want to...**

| Goal | Read This | Time |
|------|-----------|------|
| Get started quickly | [SETUP_QUICK_START.md](../SETUP_QUICK_START.md) | 10 min |
| Understand all credentials | [CREDENTIALS_AND_SETUP.md](./CREDENTIALS_AND_SETUP.md) | 30 min |
| Find exact formats | [CREDENTIALS_MATRIX.md](./CREDENTIALS_MATRIX.md) | 10 min |
| Fill in `.env` file | [.env.example](../.env.example) | 15 min |
| Troubleshoot an issue | [CREDENTIALS_AND_SETUP.md](./CREDENTIALS_AND_SETUP.md#troubleshooting) | 5-10 min |
| Deploy to production | [CREDENTIALS_AND_SETUP.md](./CREDENTIALS_AND_SETUP.md#production-environment) | 30 min |

---

## 💾 Files in This Setup

```
UATMMS/
├── .env.example              ← Copy to .env and fill in
├── SETUP_QUICK_START.md      ← Start here (5 min)
├── docker-compose.yml        ← For local dev services
├── requirements.txt          ← Python packages
└── docs/
    ├── README_CREDENTIALS.md ← This file
    ├── CREDENTIALS_AND_SETUP.md ← Detailed guide
    ├── CREDENTIALS_MATRIX.md ← Quick reference
    └── [other docs...]
```

---

## 📞 Support Resources

| Issue Type | Resource |
|-----------|----------|
| Firebase | https://firebase.google.com/support |
| PostgreSQL | https://www.postgresql.org/community |
| Redis | https://redis.io/support |
| AWS | https://aws.amazon.com/support |
| SUMO | https://sumo.dlr.de/wiki/Contact |
| Python/pip | https://python.org/help |
| Docker | https://docs.docker.com |

---

## ✅ Pre-Flight Checklist

Run before starting development:

```bash
#!/bin/bash
echo "🔍 UATMMS Pre-Flight Checklist"

# 1. Python version
echo "1. Checking Python..."
python --version | grep -q "3.1[0-9]" && echo "✅ Python OK" || echo "❌ Need Python 3.10+"

# 2. Required packages
echo "2. Checking packages..."
python -c "import sqlalchemy, firebase_admin, redis" && echo "✅ Packages OK" || echo "❌ Run: pip install -r requirements.txt"

# 3. Database
echo "3. Checking PostgreSQL..."
psql --version >/dev/null 2>&1 && echo "✅ psql OK" || echo "❌ PostgreSQL not found"

# 4. Redis
echo "4. Checking Redis..."
redis-cli --version >/dev/null 2>&1 && echo "✅ redis-cli OK" || echo "❌ Redis not found"

# 5. SUMO
echo "5. Checking SUMO..."
sumo --version >/dev/null 2>&1 && echo "✅ SUMO OK" || echo "❌ SUMO not found"

# 6. .env file
echo "6. Checking .env..."
[ -f .env ] && echo "✅ .env exists" || echo "❌ Create .env: cp .env.example .env"

echo ""
echo "🎯 Setup status complete!"
```

---

## 🎯 Next Steps

1. **Read**: Start with [SETUP_QUICK_START.md](../SETUP_QUICK_START.md)
2. **Setup**: Follow the 5-minute essentials
3. **Configure**: Copy `.env.example` to `.env` and fill in values
4. **Test**: Run the pre-flight checklist
5. **Develop**: Start coding!

---

## 📝 Document Versions

| File | Version | Last Updated | Status |
|------|---------|--------------|--------|
| README_CREDENTIALS.md | 1.0 | Oct 2026 | ✅ Complete |
| SETUP_QUICK_START.md | 1.0 | Oct 2026 | ✅ Complete |
| CREDENTIALS_AND_SETUP.md | 1.0 | Oct 2026 | ✅ Complete |
| CREDENTIALS_MATRIX.md | 1.0 | Oct 2026 | ✅ Complete |
| .env.example | 1.0 | Oct 2026 | ✅ Complete |

---

**Last Updated**: October 2026  
**For Questions**: Check the relevant document or see Support Resources above
