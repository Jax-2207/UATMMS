# UATMMS Credentials Matrix - Complete Reference

Quick-reference table of all credentials, services, and configuration needed.

## Summary Table

| Service | Component | Credential Type | Required | Dev | Prod | Where to Get | Example |
|---------|-----------|-----------------|----------|-----|------|--------------|---------|
| **Firebase** | Authentication | Service Account JSON | ✅ | ✅ | ✅ | Firebase Console → Service Accounts | `{"type":"service_account",...}` |
| **Firebase** | Project ID | String | ❌ | ✅ | ✅ | Firebase Console → Settings | `uatmms-project-id` |
| **PostgreSQL** | Database URL | Connection String | ✅ | ✅ | ✅ | Create database & user | `postgresql://user:pass@host:5432/db` |
| **PostgreSQL** | Host | String | ✅ | ✅ | ✅ | Local/Cloud | `localhost` or `db.example.com` |
| **PostgreSQL** | Port | Number | ✅ | ✅ | ✅ | Database config | `5432` |
| **PostgreSQL** | Username | String | ✅ | ✅ | ✅ | Create database user | `uatmms_user` |
| **PostgreSQL** | Password | String | ✅ | ✅ | ✅ | Set during user creation | `uatmms_pass` (strong in prod) |
| **PostgreSQL** | Database Name | String | ✅ | ✅ | ✅ | Create database | `uatmms_db` |
| **Redis** | Connection URL | URL | ✅ | ✅ | ✅ | Redis server or managed service | `redis://localhost:6379/0` |
| **Redis** | Host | String | ✅ | ✅ | ✅ | Local/Cloud | `localhost` or `redis.example.com` |
| **Redis** | Port | Number | ✅ | ✅ | ✅ | Redis config | `6379` |
| **Redis** | Database | Number | ❌ | ✅ | ✅ | Redis config | `0` |
| **Redis** | Password | String | ❌ | ❌ | ✅ | Set in Redis config | `your-redis-password` |
| **AWS S3** | Access Key ID | String | ❌ | ❌ | ✅ | AWS IAM → Create User | `AKIAIOSFODNN7EXAMPLE` |
| **AWS S3** | Secret Access Key | String | ❌ | ❌ | ✅ | AWS IAM → Generate Keys | `wJalrXUt...` |
| **AWS S3** | Region | String | ❌ | ❌ | ✅ | Choose during bucket creation | `us-east-1` |
| **AWS S3** | Bucket Name | String | ❌ | ❌ | ✅ | Create S3 bucket | `uatmms-models` |
| **AWS S3** | Model Prefix | String | ❌ | ❌ | ✅ | Your convention | `models/` |
| **SUMO** | Installation Path | File Path | ✅ | ✅ | ✅ | Installation directory | `/opt/sumo` or `C:\Program Files\SUMO` |
| **SUMO** | Binary Path | File Path | ✅ | ✅ | ✅ | SUMO bin directory | `/opt/sumo/bin/sumo` |
| **SUMO** | Network File | File Path | ✅ | ✅ | ✅ | Your network data | `data/bangalore.net.xml` |
| **SUMO** | Route File | File Path | ✅ | ✅ | ✅ | Your route data | `data/bangalore.rou.xml` |
| **App** | Secret Key | String | ✅ | ✅ | ✅ | Generate random | `your-secret-key-here` |
| **App** | JWT Secret | String | ✅ | ✅ | ✅ | Generate random | `jwt-secret-key` |
| **App** | Environment | String | ✅ | ✅ | ✅ | Your choice | `development` or `production` |

---

## Detailed Credential Specifications

### 1. Firebase Service Account

**What It Is**: JSON key for server-side Firebase Admin SDK authentication

**Required Fields**:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

**How to Get**:
1. Go to Firebase Console
2. Project Settings → Service Accounts
3. Click "Generate New Private Key"
4. Save JSON file

**Size**: ~2-3 KB  
**Sensitivity**: 🔴 CRITICAL - Treat like password  
**Rotation**: Every 3-6 months  
**Environment Variable**: `FIREBASE_CREDENTIALS_JSON` or `FIREBASE_CREDENTIALS_FILE`

---

### 2. PostgreSQL Connection

**Format**: `postgresql://username:password@host:port/database`

**Example**:
```
postgresql://uatmms_user:MyStr0ng!Pass@db.example.com:5432/uatmms_db
```

**Components**:
| Component | Example | Notes |
|-----------|---------|-------|
| Username | `uatmms_user` | Min 8 chars, strong in prod |
| Password | `MyStr0ng!Pass` | 16+ chars, mixed case, symbols |
| Host | `localhost` | `db.example.com` for cloud |
| Port | `5432` | Default PostgreSQL port |
| Database | `uatmms_db` | Created beforehand |

**How to Create**:
```bash
# Using psql:
createuser uatmms_user
createdb uatmms_db -O uatmms_user
psql -U postgres -d postgres \
  -c "ALTER USER uatmms_user WITH PASSWORD 'MyStr0ng!Pass'"

# Verify:
psql postgresql://uatmms_user:MyStr0ng!Pass@localhost:5432/uatmms_db -c "SELECT 1"
```

**Sensitivity**: 🔴 CRITICAL - Database root access  
**Rotation**: Every 90 days (production)  
**Backup**: Store in password manager

---

### 3. Redis Connection

**Format**: `redis://:password@host:port/db`

**Example**:
```
redis://:RedisP@ss@redis.example.com:6379/0
```

**Components**:
| Component | Example | Notes |
|-----------|---------|-------|
| Host | `localhost` | `redis.example.com` for cloud |
| Port | `6379` | Default Redis port |
| Password | `RedisP@ss` | Optional, required in prod |
| Database | `0` | 0-15 available |

**How to Set Password**:
```bash
# In redis.conf:
requirepass RedisP@ss

# Or via redis-cli:
redis-cli CONFIG SET requirepass "RedisP@ss"
```

**Sensitivity**: 🟠 HIGH - Cache data access  
**Rotation**: Every 6 months  
**Backup**: Store in password manager

---

### 4. AWS S3 Credentials

**Components**:
- **Access Key ID**: Public identifier (20 chars)
- **Secret Access Key**: Private key (40 chars)
- **Region**: AWS region code
- **Bucket**: S3 bucket name

**Example**:
```
Access Key: AKIAIOSFODNN7EXAMPLE
Secret: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Region: us-east-1
Bucket: uatmms-models
```

**How to Generate**:
1. AWS Console → IAM → Users
2. Create user: `uatmms-app`
3. Attach policy: `AmazonS3FullAccess` (or custom)
4. Create access keys
5. Save Access Key ID and Secret Access Key

**Sensitivity**: 🔴 CRITICAL - AWS account access  
**Rotation**: Every 3 months  
**Backup**: AWS Secrets Manager

---

### 5. SUMO Paths

**Components**:
| Component | Example | Purpose |
|-----------|---------|---------|
| SUMO_HOME | `/opt/sumo` or `C:\Program Files\SUMO` | Installation directory |
| SUMO_BINARY | `/opt/sumo/bin/sumo` | Executable path |
| Network File | `data/bangalore_core.net.xml` | Network topology |
| Route File | `data/bangalore_routes.rou.xml` | Vehicle routes |

**How to Verify**:
```bash
# Check installation
$SUMO_BINARY --version

# Check network file exists
ls -la data/bangalore_core.net.xml

# Check route file exists
ls -la data/bangalore_routes.rou.xml
```

**Sensitivity**: 🟢 LOW - Public paths  
**Backup**: Version control (git)

---

### 6. Application Secrets

**Secret Key**: Used for session management, CSRF tokens

**How to Generate**:
```python
import secrets
print(secrets.token_urlsafe(32))  # Generates 32-byte random key
```

**JWT Secret**: Used for token signing

**How to Generate**:
```bash
openssl rand -hex 32
# Output: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**Sensitivity**: 🔴 CRITICAL - Application security  
**Rotation**: When compromised or annually  
**Backup**: AWS Secrets Manager / Azure Key Vault

---

## Environment Variables by Phase

### Phase 1-3: Core Traffic
```bash
SUMO_HOME="/opt/sumo"
SUMO_BINARY="/opt/sumo/bin/sumo"
SIMULATION_NETWORK_FILE="data/network.net.xml"
SIMULATION_ROUTE_FILE="data/routes.rou.xml"
```

### Phase 4-5: Incidents & Emergencies
```bash
DATABASE_URL="postgresql://..."
INCIDENT_DETECTION_THRESHOLD="0.8"
EMERGENCY_CORRIDOR_MAX_DEVICES="10"
```

### Phase 6: Traffic Prediction
```bash
PREDICTION_MODEL_TYPE="xgboost"
PREDICTION_LOOKBACK_HOURS="24"
PREDICTION_FORECAST_HOURS="1"
```

### Phase 7: Reinforcement Learning
```bash
PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512"
RL_ALGORITHM="ppo"
RL_TOTAL_TIMESTEPS="1000000"
S3_BUCKET="uatmms-models"
AWS_ACCESS_KEY_ID="AKIA..."
AWS_SECRET_ACCESS_KEY="..."
```

### Phase 8: Database & Auth
```bash
DATABASE_URL="postgresql://..."
FIREBASE_CREDENTIALS_JSON="..."
SECRET_KEY="..."
JWT_SECRET_KEY="..."
REDIS_URL="redis://..."
```

### Phase 9: Dashboard
```bash
REDIS_URL="redis://..."
WEBSOCKET_ENABLED="true"
DASHBOARD_UPDATE_FREQUENCY="5"
```

### Phase 10: 3D Twin
```bash
TWIN_ENABLED="true"
TWIN_UPDATE_FREQUENCY="10"
TWIN_LOD_LEVELS="4"
```

---

## Credential Checklist

### Before Development
- [ ] Firebase service account JSON downloaded
- [ ] PostgreSQL database created and accessible
- [ ] Redis running and accessible
- [ ] SUMO installed and verified
- [ ] `.env` file created with all Phase 1-3 variables
- [ ] Python dependencies installed

### Before Phase 8 (Database & Auth)
- [ ] Firebase credentials added to `.env`
- [ ] PostgreSQL connection tested
- [ ] Redis connection tested
- [ ] Application secret key generated

### Before Phase 7 (RL & Model Training)
- [ ] PyTorch installed with GPU support (if available)
- [ ] AWS S3 bucket created (for production)
- [ ] AWS IAM user and keys generated
- [ ] S3 credentials added to `.env`

### Before Production Deployment
- [ ] All credentials rotated (fresh keys)
- [ ] Credentials stored in AWS Secrets Manager or similar
- [ ] `.env` never committed to git
- [ ] SSL/TLS certificates obtained
- [ ] Database backups configured
- [ ] Monitoring and logging enabled
- [ ] Credentials audit completed

---

## Security Best Practices

1. **Never Log Credentials**
   - ❌ Don't print in logs
   - ❌ Don't commit to git
   - ❌ Don't share in chat/email
   - ✅ Use environment variables only

2. **Rotate Regularly**
   - Firebase keys: Every 3-6 months
   - AWS keys: Every 3 months
   - Database passwords: Every 90 days
   - Application secrets: When suspected breach

3. **Use Different Credentials**
   - Development: Separate project/resources
   - Staging: Separate credentials
   - Production: Highest security, separate project
   - Never reuse credentials across environments

4. **Store Securely**
   - ✅ AWS Secrets Manager
   - ✅ Azure Key Vault
   - ✅ HashiCorp Vault
   - ❌ Plaintext files
   - ❌ Git repositories
   - ❌ Email/chat

5. **Audit Access**
   - Log all credential usage
   - Monitor for unusual patterns
   - Set up alerts for failed authentication
   - Review access logs regularly

---

## Troubleshooting Credentials

| Issue | Cause | Solution |
|-------|-------|----------|
| Firebase auth fails | Invalid JSON | Verify JSON syntax: `python -c "import json; json.load(open('key.json'))"` |
| DB connection refused | Wrong password | Verify with: `psql postgresql://user:pass@host/db` |
| DB connection timeout | Wrong host | Check host is reachable: `ping host` |
| Redis unreachable | Wrong port | Check Redis is listening: `redis-cli ping` |
| S3 access denied | Invalid keys | Verify IAM policy includes S3 permissions |
| SUMO not found | Wrong path | Find SUMO: `which sumo` and update `SUMO_BINARY` |
| JWT errors | Expired secret | Regenerate using `openssl rand -hex 32` |

---

## References

- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
- [PostgreSQL Authentication](https://www.postgresql.org/docs/current/auth-password.html)
- [Redis Security](https://redis.io/topics/security)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [SUMO Installation](https://sumo.dlr.de/wiki/Downloads)

---

**Last Updated**: October 2026  
**Version**: 1.0  
**Status**: Complete
