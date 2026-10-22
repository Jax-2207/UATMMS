# UATMMS: Credentials, Keys & Setup Requirements

Complete guide to all external accounts, API credentials, and configuration needed to run the Universal Automatic Traffic Management System (UATMMS) across all phases.

---

## Table of Contents

1. [Authentication & Authorization](#authentication--authorization)
2. [Database & Storage](#database--storage)
3. [Traffic Simulation](#traffic-simulation)
4. [Machine Learning & Model Management](#machine-learning--model-management)
5. [Infrastructure & DevOps](#infrastructure--devops)
6. [Environment Variables](#environment-variables)
7. [Setup Checklist](#setup-checklist)
8. [Development vs Production](#development-vs-production)

---

## Authentication & Authorization

### Firebase Admin SDK

**Purpose**: User authentication, role-based access control (RBAC), and session management

**What You Need**:
- Firebase Project (free tier available at https://firebase.google.com)
- Firebase Service Account credentials JSON file

**Setup Steps**:
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create a new project (or use existing)
3. Enable Authentication:
   - Go to **Authentication** → **Sign-in method**
   - Enable **Email/Password**
   - Enable **Anonymous** (optional, for testing)
   - Enable **Google** (optional)
4. Create a Service Account:
   - Go to **Project Settings** → **Service Accounts**
   - Click **Generate New Private Key**
   - Save the JSON file securely
5. Enable Firestore/Realtime Database (optional, for audit logs):
   - Go to **Firestore Database** or **Realtime Database**
   - Start in test mode initially

**Environment Variable**:
```bash
FIREBASE_CREDENTIALS_JSON="<full JSON content or path to file>"
# Or use file path:
FIREBASE_CREDENTIALS_FILE="/path/to/serviceAccountKey.json"
```

**Example Credentials File**:
```json
{
  "type": "service_account",
  "project_id": "uatmms-project-id",
  "private_key_id": "key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@uatmms-project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

**Security Notes**:
- ⚠️ Never commit serviceAccountKey.json to git
- Store in environment variables only
- Rotate keys regularly in production
- Use different projects for dev/staging/production

---

## Database & Storage

### PostgreSQL (Primary Database)

**Purpose**: Store users, roles, permissions, network topology, incidents, emergencies, audit logs, simulation runs, models

**What You Need**:
- PostgreSQL 14+ server
- Database user credentials
- Database name

**Local Setup** (Development):
```bash
# Using Docker (recommended)
docker run --name uatmms-postgres \
  -e POSTGRES_USER=uatmms_user \
  -e POSTGRES_PASSWORD=uatmms_pass \
  -e POSTGRES_DB=uatmms_db \
  -p 5432:5432 \
  -d postgres:16

# Or install PostgreSQL locally
# Windows: https://www.postgresql.org/download/windows/
# macOS: brew install postgresql@16
# Linux: apt-get install postgresql postgresql-contrib
```

**Environment Variables**:
```bash
DATABASE_URL="postgresql://uatmms_user:uatmms_pass@localhost:5432/uatmms_db"
# Or components:
DB_HOST="localhost"
DB_PORT="5432"
DB_USER="uatmms_user"
DB_PASSWORD="uatmms_pass"
DB_NAME="uatmms_db"
```

**Production Setup**:
- AWS RDS PostgreSQL
- Azure Database for PostgreSQL
- Google Cloud SQL
- DigitalOcean Managed Database

**Example Connection String**:
```
postgresql://user:password@db.example.com:5432/uatmms_prod
```

**Database Initialization**:
```bash
# Create database
createdb uatmms_db -U uatmms_user

# Run migrations (Alembic)
alembic upgrade head

# Seed initial data (roles, permissions, etc.)
python scripts/seed_rbac.py
```

### Redis (Caching & Session Store)

**Purpose**: Cache traffic metrics, store WebSocket connections, rate limiting

**What You Need**:
- Redis 7+ server
- Redis connection string

**Local Setup**:
```bash
# Using Docker (recommended)
docker run --name uatmms-redis \
  -p 6379:6379 \
  -d redis:7-alpine

# Or install locally
# Windows: Download from https://github.com/microsoftarchive/redis/releases
# macOS: brew install redis
# Linux: apt-get install redis-server
```

**Environment Variables**:
```bash
REDIS_URL="redis://localhost:6379/0"
# Or with authentication:
REDIS_URL="redis://:password@localhost:6379/0"
```

**Production Setup**:
- AWS ElastiCache
- Azure Cache for Redis
- Google Cloud Memorystore
- DigitalOcean Managed Redis

### S3 or Cloud Storage (Model Artifacts)

**Purpose**: Store trained RL models, checkpoints, training logs

**What You Need**:
- AWS S3 bucket OR equivalent (Google Cloud Storage, Azure Blob)
- API credentials (access key, secret key)
- Bucket name

**AWS S3 Setup**:
1. Create AWS Account at https://aws.amazon.com
2. Create S3 bucket:
   - Bucket name: `uatmms-models` (or similar)
   - Region: Same as deployment region
   - Block public access: Yes
3. Create IAM user with S3 access:
   - Go to IAM → Users → Create user
   - Attach policy: `AmazonS3FullAccess` (or custom policy)
   - Create access key
   - Save Access Key ID and Secret Access Key

**Environment Variables**:
```bash
AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
AWS_REGION="us-east-1"
S3_BUCKET="uatmms-models"
S3_MODEL_PREFIX="models/"  # Path prefix in bucket
```

**Example S3 Paths**:
```
s3://uatmms-models/models/ppo_j1_v1.zip
s3://uatmms-models/checkpoints/ppo_j1_checkpoint_12.pth
s3://uatmms-models/logs/training_2024-10-22.log
```

---

## Traffic Simulation

### SUMO (Simulation of Urban MObility)

**Purpose**: Traffic simulation engine for Phase 1-7 (network topology, traffic generation, signal control)

**What You Need**:
- SUMO 1.28.0+
- TraCI (Traffic Control Interface) Python bindings
- Network files (OSM, NET, TAZ, POI)

**Installation**:

**Windows**:
```bash
# Download and install
# https://sumo.dlr.de/download/

# Or use Anaconda/pip
conda install -c conda-forge sumo

# Verify installation
sumo --version
```

**macOS**:
```bash
brew install sumo
sumo --version
```

**Linux**:
```bash
apt-get install sumo
sumo --version
```

**Environment Variables**:
```bash
SUMO_HOME="/opt/sumo"  # or C:\Program Files\SUMO on Windows
SUMO_BINARY="/opt/sumo/bin/sumo"  # or sumo.exe on Windows
```

**Network Files**:
- Network file (`.net.xml`): Intersection and road topology
- Route file (`.rou.xml`): Vehicle routes and demand
- Config file (`.sumocfg`): Simulation parameters
- Additional Files (`.taz.xml`, `.poly.xml`): Traffic analysis zones, POIs

**Example Network Structure**:
```
data/
├── bangalore_network/
│   ├── bangalore_core.net.xml      # Network topology
│   ├── bangalore_routes.rou.xml    # Vehicle routes
│   ├── bangalore.sumocfg           # SUMO config
│   ├── bangalore.taz.xml           # Traffic analysis zones
│   └── bangalore_poi.poly.xml      # Points of interest
└── simulation_configs/
    ├── peak_rush_config.py
    └── off_peak_config.py
```

**Getting Network Files**:
1. **OpenStreetMap (OSM)**:
   - Download from [OSM](https://www.openstreetmap.org)
   - Convert using `netconvert`:
     ```bash
     netconvert -c osm_file.osm -o network.net.xml
     ```

2. **Built-in Networks**:
   - SUMO includes sample networks in `$SUMO_HOME/data/networks/`

3. **Generate Programmatically**:
   - Use SUMO's `netedit` GUI
   - Or generate with scripts

---

## Machine Learning & Model Management

### PyTorch

**Purpose**: Deep reinforcement learning (Phase 7)

**What You Need**:
- PyTorch 2.3.0+
- CUDA 12.1 (for GPU acceleration, optional but recommended)

**Installation**:
```bash
# CPU only
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# GPU (CUDA 12.1)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
```

**Environment Variables**:
```bash
PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512"  # For GPU memory optimization
TORCH_HOME="/path/to/torch/cache"  # Pre-trained models cache
```

### Stable Baselines3

**Purpose**: RL algorithms (PPO, DQN, etc.)

**Installation**:
```bash
pip install stable-baselines3[extra]>=2.4.0
```

**Model Storage**:
- Trained models saved as `.zip` files
- Stored in S3 or local filesystem
- Include metadata: reward, safety violations, training steps

**Example Model File**:
```
ppo_j1_v1.zip          # Contains model weights + config
├── policy.zip
└── policy.pth
```

### Scikit-Learn & XGBoost (Phase 6)

**Purpose**: Traffic prediction baseline models

**Installation**:
```bash
pip install scikit-learn xgboost
```

**Trained Models Storage**:
- Pickle format (`.pkl`)
- Joblib format (`.joblib`)
- Stored in S3 or local filesystem

---

## Infrastructure & DevOps

### Docker (Containerization)

**Purpose**: Containerize backend, simulate production locally

**What You Need**:
- Docker Desktop or Docker Engine
- Docker Compose 2.0+

**Installation**:
- Windows: [Docker Desktop](https://www.docker.com/products/docker-desktop)
- macOS: [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Linux: `apt-get install docker.io docker-compose`

**Docker Compose File** (for local development):
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
      - redis_data:/data

  backend:
    build: ./backend
    environment:
      DATABASE_URL: "postgresql://uatmms_user:uatmms_pass@postgres:5432/uatmms_db"
      REDIS_URL: "redis://redis:6379/0"
      FIREBASE_CREDENTIALS_JSON: ${FIREBASE_CREDENTIALS_JSON}
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
  redis_data:
```

### Git & Version Control

**Purpose**: Source code management

**What You Need**:
- Git credentials (SSH key or Personal Access Token)
- GitHub/GitLab/Bitbucket account

**GitHub Setup**:
1. Create account at https://github.com
2. Generate SSH key:
   ```bash
   ssh-keygen -t ed25519 -C "your-email@example.com"
   ```
3. Add SSH key to GitHub Settings → SSH Keys
4. Clone repository:
   ```bash
   git clone git@github.com:your-org/UATMMS.git
   ```

### CI/CD Pipeline (GitHub Actions / GitLab CI)

**Purpose**: Automated testing and deployment

**What You Need**:
- GitHub Actions (built-in) OR GitLab CI
- Docker Hub credentials (optional, for pushing images)
- AWS/Azure/GCP credentials (for deployment)

---

## Environment Variables

### Complete `.env` File Template

```bash
# ============================================================================
# Firebase Authentication
# ============================================================================
FIREBASE_CREDENTIALS_JSON='{"type":"service_account",...}'
FIREBASE_CREDENTIALS_FILE="/path/to/serviceAccountKey.json"
FIREBASE_PROJECT_ID="uatmms-project-id"

# ============================================================================
# Database
# ============================================================================
DATABASE_URL="postgresql://uatmms_user:uatmms_pass@localhost:5432/uatmms_db"
DB_HOST="localhost"
DB_PORT="5432"
DB_USER="uatmms_user"
DB_PASSWORD="uatmms_pass"
DB_NAME="uatmms_db"
DB_POOL_SIZE="20"
DB_POOL_RECYCLE="3600"

# ============================================================================
# Redis Cache
# ============================================================================
REDIS_URL="redis://localhost:6379/0"
REDIS_HOST="localhost"
REDIS_PORT="6379"
REDIS_DB="0"
REDIS_PASSWORD=""  # Optional

# ============================================================================
# AWS S3 (Model Storage)
# ============================================================================
AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
AWS_REGION="us-east-1"
S3_BUCKET="uatmms-models"
S3_MODEL_PREFIX="models/"
S3_ENDPOINT_URL=""  # Optional, for S3-compatible services

# ============================================================================
# SUMO Traffic Simulation
# ============================================================================
SUMO_HOME="/opt/sumo"
SUMO_BINARY="/opt/sumo/bin/sumo"
SIMULATION_NETWORK_FILE="/data/bangalore_network/bangalore_core.net.xml"
SIMULATION_ROUTE_FILE="/data/bangalore_network/bangalore_routes.rou.xml"
SIMULATION_SEED="42"

# ============================================================================
# Application Configuration
# ============================================================================
APP_ENV="development"  # development, staging, production
APP_DEBUG="true"
APP_LOG_LEVEL="INFO"
SECRET_KEY="your-secret-key-here-change-in-production"
ALLOWED_HOSTS="localhost,127.0.0.1,yourdomain.com"

# ============================================================================
# API Configuration
# ============================================================================
API_VERSION="v1"
API_TITLE="UATMMS"
API_BASE_URL="http://localhost:8000"
CORS_ORIGINS="http://localhost:3000,http://localhost:5173"

# ============================================================================
# Backend Server
# ============================================================================
BACKEND_HOST="0.0.0.0"
BACKEND_PORT="8000"
WORKERS="4"

# ============================================================================
# ML/RL Configuration
# ============================================================================
PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512"
TORCH_HOME="/tmp/torch_cache"
MODEL_TRAINING_STEPS="1000000"
MODEL_EVAL_EPISODES="100"

# ============================================================================
# Security
# ============================================================================
JWT_SECRET_KEY="your-jwt-secret-key-here"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_HOURS="24"
BCRYPT_ROUNDS="12"

# ============================================================================
# Monitoring & Logging
# ============================================================================
SENTRY_DSN=""  # Optional, for error tracking
LOG_FILE="/var/log/uatmms.log"
ENABLE_METRICS="true"

# ============================================================================
# Feature Flags
# ============================================================================
ENABLE_PHASE_1_NETWORK_TOPOLOGY="true"
ENABLE_PHASE_2_TRAFFIC_GENERATION="true"
ENABLE_PHASE_3_SAFETY_CORRIDORS="true"
ENABLE_PHASE_4_INCIDENT_DETECTION="true"
ENABLE_PHASE_5_EMERGENCY_CORRIDORS="true"
ENABLE_PHASE_6_PREDICTION="true"
ENABLE_PHASE_7_RL="true"
ENABLE_PHASE_8_DATABASE_AUTH="true"
ENABLE_PHASE_9_DASHBOARD="true"
ENABLE_PHASE_10_3D_TWIN="true"
```

### Create `.env` File

```bash
# Create file in project root
cp .env.example .env

# Edit with your credentials
nano .env
# or
code .env
```

---

## Setup Checklist

### Pre-Deployment Checklist

- [ ] **Firebase Project**
  - [ ] Project created
  - [ ] Service account JSON downloaded
  - [ ] Authentication enabled (Email/Password)
  - [ ] Database created (optional)

- [ ] **PostgreSQL Database**
  - [ ] Server running (local or cloud)
  - [ ] Database created
  - [ ] User credentials set
  - [ ] Migrations applied (`alembic upgrade head`)

- [ ] **Redis Cache**
  - [ ] Server running
  - [ ] Connection tested

- [ ] **AWS S3** (if using)
  - [ ] Bucket created
  - [ ] IAM user created
  - [ ] Access credentials generated
  - [ ] Bucket policy configured

- [ ] **SUMO Simulation**
  - [ ] SUMO installed and verified
  - [ ] Network files downloaded/created
  - [ ] TraCI Python bindings working

- [ ] **Environment Variables**
  - [ ] `.env` file created
  - [ ] All credentials filled in
  - [ ] No credentials committed to git

- [ ] **Python Dependencies**
  - [ ] Python 3.10+ installed
  - [ ] Virtual environment created
  - [ ] `pip install -r requirements.txt` successful
  - [ ] Firebase admin SDK installed
  - [ ] All Phase packages installed

- [ ] **Database Initialization**
  - [ ] Tables created
  - [ ] Initial RBAC roles/permissions seeded
  - [ ] Admin user created

- [ ] **Git Setup**
  - [ ] Repository cloned
  - [ ] SSH keys configured
  - [ ] `.env` added to `.gitignore`

---

## Development vs Production

### Development Environment

**Database**: PostgreSQL (Docker recommended)
```bash
docker run --name uatmms-dev-db \
  -e POSTGRES_USER=dev_user \
  -e POSTGRES_PASSWORD=dev_pass \
  -e POSTGRES_DB=uatmms_dev \
  -p 5432:5432 \
  -d postgres:16
```

**Firebase**: Firebase Console with test project
- Use test authentication rules
- Allow anonymous access for testing

**S3**: LocalStack for local S3 simulation
```bash
docker run -p 4566:4566 -d localstack/localstack:latest
```

**Environment**:
```bash
APP_ENV="development"
DEBUG=true
DATABASE_URL="postgresql://dev_user:dev_pass@localhost:5432/uatmms_dev"
```

### Production Environment

**Database**: AWS RDS / Azure Database / Cloud SQL
- Daily backups
- Multi-AZ for redundancy
- Encrypted credentials

**Firebase**: Production Firebase project
- Strong authentication rules
- Disable anonymous access
- Use custom domain

**S3**: AWS S3 with versioning & encryption
- Versioning enabled
- Server-side encryption
- CloudFront CDN for model distribution

**Environment**:
```bash
APP_ENV="production"
DEBUG=false
DATABASE_URL="postgresql://prod_user:${DB_PASSWORD}@db.prod.internal:5432/uatmms"
# Use AWS Secrets Manager or similar
```

---

## Troubleshooting

### Firebase Authentication Issues

**Problem**: "Failed to initialize Firebase"
```
Solution: Check FIREBASE_CREDENTIALS_JSON is valid JSON and has correct permissions
```

**Problem**: "Invalid or expired authentication token"
```
Solution: Token may be expired (24hr default). Refresh by re-authenticating
```

### Database Connection Issues

**Problem**: "Connection refused to PostgreSQL"
```
Solution: 
1. Verify PostgreSQL is running: psql --version
2. Check DATABASE_URL format
3. Verify credentials are correct
```

**Problem**: "Alembic migration fails"
```
Solution:
1. Check database schema version: alembic current
2. Manually check for conflicts: alembic history
3. Downgrade if needed: alembic downgrade -1
```

### S3 Connection Issues

**Problem**: "Access Denied to S3 bucket"
```
Solution:
1. Verify AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
2. Check IAM user has S3 permissions
3. Verify bucket policy allows access
```

### SUMO Simulation Issues

**Problem**: "TraCI connection refused"
```
Solution:
1. Verify SUMO_BINARY path is correct
2. Check network and route files exist
3. Ensure port 9999 (TraCI default) is available
```

---

## Security Best Practices

1. **Credentials Management**
   - ✅ Use environment variables (never hardcode)
   - ✅ Use `.gitignore` for sensitive files
   - ✅ Rotate keys periodically
   - ✅ Use separate credentials for dev/prod

2. **Database Security**
   - ✅ Use strong passwords (16+ chars, mixed)
   - ✅ Enable SSL connections
   - ✅ Restrict database access by IP
   - ✅ Enable audit logging
   - ✅ Regular backups

3. **API Security**
   - ✅ Use HTTPS in production
   - ✅ Implement rate limiting
   - ✅ Validate all inputs
   - ✅ Use strong JWT secrets
   - ✅ Enable CORS only for trusted domains

4. **Firebase Security**
   - ✅ Use service account JSON (not exposed in code)
   - ✅ Set appropriate Firebase rules
   - ✅ Regularly audit access
   - ✅ Monitor usage patterns

---

## References

- [Firebase Documentation](https://firebase.google.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs)
- [Redis Documentation](https://redis.io/documentation)
- [SUMO Documentation](https://sumo.dlr.de/docs)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3)
- [Docker Documentation](https://docs.docker.com)
- [PyTorch Documentation](https://pytorch.org/docs)

---

## Support

For issues with credential setup, contact:
- Firebase Support: https://firebase.google.com/support
- AWS Support: https://aws.amazon.com/support
- PostgreSQL Community: https://www.postgresql.org/community
- SUMO Community: https://sumo.dlr.de/wiki/Contact

Last Updated: October 2026
