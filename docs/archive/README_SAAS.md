# 🛍️ Salla Price Optimizer - Multi-Tenant SaaS Platform

**Automated AI-Powered Price Optimization for Salla Stores**

Transform your single-store price optimizer into a fully automated, multi-tenant SaaS platform that serves unlimited Salla stores with complete data isolation and automated background processing.

---

## 🌟 Features

### ✅ Multi-Tenant Architecture
- **Unlimited Stores**: Support multiple Salla stores simultaneously
- **Data Isolation**: Each store's data is completely isolated
- **OAuth Integration**: Seamless Salla app authorization
- **Automatic Onboarding**: Users authorize once, system handles everything

### ✅ Automated Background Processing
- **Scheduled Optimization**: Runs every 6-12 hours automatically
- **Task Queue**: Celery + Redis for reliable job processing
- **Concurrent Processing**: Handle multiple stores simultaneously
- **Error Recovery**: Automatic retry and error handling

### ✅ Intelligent Pricing
- **AI-Powered Analysis**: CrewAI multi-agent system
- **Competitor Tracking**: Real-time market intelligence
- **Risk Assessment**: Low/Medium/High risk classification
- **Profit Protection**: Minimum margin enforcement

### ✅ Production Ready
- **PostgreSQL Database**: Scalable data storage
- **Docker Support**: Easy deployment with Docker Compose
- **Monitoring**: Celery Flower for task monitoring
- **Logging**: Comprehensive activity logs

---

## 🏗️ Architecture

```
User → OAuth → FastAPI → Database
                  ↓
            Celery Tasks
                  ↓
         Multi-Tenant Optimizer
                  ↓
         CrewAI Agents → Salla API
```

**Components:**
1. **FastAPI** - OAuth handler & API endpoints
2. **PostgreSQL** - Multi-tenant database
3. **Redis** - Task queue & caching
4. **Celery** - Background job processing
5. **CrewAI** - AI agent orchestration
6. **Streamlit** - User dashboard (optional)

---

## 📦 Installation

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Redis 7+
- Docker (optional)

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/yourusername/salla-price-optimizer.git
cd salla-price-optimizer

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements_saas.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 5. Initialize system
python init_saas.py

# 6. Start services (see below)
```

---

## ⚙️ Configuration

Create `.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/salla_optimizer

# Redis
REDIS_URL=redis://localhost:6379/0

# API Keys
OPENAI_API_KEY=sk-proj-your-key
TAVILY_API_KEY=tvly-your-key

# OAuth
OAUTH_CALLBACK_URL=http://localhost:8000/oauth/callback

# Optional
SENTRY_DSN=your-sentry-dsn
```

---

## 🚀 Running the System

### Option 1: Manual Start

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: FastAPI
uvicorn api.oauth_handler:app --reload --port 8000

# Terminal 3: Celery Worker
celery -A scheduler.celery_app worker --loglevel=info

# Terminal 4: Celery Beat
celery -A scheduler.celery_app beat --loglevel=info

# Terminal 5: Flower (optional)
celery -A scheduler.celery_app flower --port=5555
```

### Option 2: Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 📊 Usage

### 1. Store Onboarding

**User Flow:**
1. User visits: `http://localhost:8000/oauth/authorize`
2. Redirected to Salla authorization page
3. User approves app permissions
4. System captures OAuth tokens
5. Store automatically onboarded
6. User redirected to dashboard

**What Happens:**
- OAuth tokens stored in database
- Store settings initialized
- Default configuration applied
- Activity logged

### 2. Automated Optimization

**Automatic Schedule:**
- Every 6 hours: Optimize all active stores
- Every hour: Check stores needing optimization
- Daily at 2 AM: Refresh expired tokens
- Weekly: Cleanup old data

**Manual Trigger:**
```python
from scheduler.tasks import manual_optimize
manual_optimize.delay("store_id_here")
```

### 3. Monitoring

**Celery Flower UI:**
```
http://localhost:5555
```

**API Endpoints:**
```bash
# Health check
curl http://localhost:8000/health

# List stores
curl http://localhost:8000/stores

# Get store details
curl http://localhost:8000/stores/{store_id}
```

---

## 🗄️ Database Schema

### Main Tables

**stores** - Store credentials & settings
```sql
- store_id (PK)
- access_token, refresh_token
- automation_mode (manual/semi-auto/full-auto)
- min_profit_margin
- update_frequency_hours
```

**products** - Store-specific products
```sql
- store_id, product_id (PK)
- name, price, cost_price
- is_tracked
```

**competitors** - Competitor pricing
```sql
- store_id, product_id
- competitor_name, price
- confidence_score
```

**pricing_decisions** - Audit trail
```sql
- store_id, product_id
- old_price, suggested_price
- strategy_used, risk_level
- action_taken
```

**optimization_runs** - Job history
```sql
- store_id, run_type
- status, duration
- products_analyzed, products_updated
```

---

## 🔐 Security

### Data Isolation
- Each store has isolated database records
- Separate output directories per store
- No cross-store data access

### Token Management
- Encrypted storage in database
- Automatic token refresh
- Expiration tracking

### Activity Logging
- All actions logged
- Audit trail maintained
- User activity tracked

---

## 📈 Scaling

### Small Scale (1-10 stores)
```
1 API server
2 Celery workers
1 PostgreSQL
1 Redis
```

### Medium Scale (10-100 stores)
```
2-3 API servers (load balanced)
4-8 Celery workers
PostgreSQL with replicas
Redis cluster
```

### Large Scale (100+ stores)
```
Auto-scaling API servers
10+ Celery workers
PostgreSQL cluster
Redis cluster
CDN for static assets
```

---

## 🛠️ Development

### Project Structure

```
salla-price-optimizer/
├── api/
│   └── oauth_handler.py          # FastAPI OAuth handler
├── database/
│   ├── schema.sql                # Database schema
│   ├── models.py                 # SQLAlchemy models
│   └── db.py                     # Database utilities
├── scheduler/
│   ├── celery_app.py             # Celery configuration
│   └── tasks.py                  # Background tasks
├── optimizer/
│   ├── multi_tenant_optimizer.py # Store-specific optimizer
│   └── token_manager.py          # Token refresh
├── agents/                       # CrewAI agents (existing)
├── tools/                        # Agent tools (existing)
├── store-data/                   # Store-specific outputs
│   ├── store_123/
│   ├── store_456/
│   └── store_789/
├── docker-compose.yml            # Docker configuration
├── requirements_saas.txt         # Dependencies
├── init_saas.py                  # Initialization script
└── README_SAAS.md               # This file
```

### Adding New Features

1. **New API Endpoint:**
```python
# api/oauth_handler.py
@app.get("/new-endpoint")
async def new_endpoint():
    return {"message": "Hello"}
```

2. **New Background Task:**
```python
# scheduler/tasks.py
@celery_app.task
def new_task():
    # Task logic here
    pass
```

3. **New Database Table:**
```python
# database/models.py
class NewTable(Base):
    __tablename__ = 'new_table'
    # Define columns
```

---

## 🧪 Testing

```bash
# Run tests
pytest

# Test specific module
pytest tests/test_oauth.py

# Test with coverage
pytest --cov=api --cov=scheduler
```

---

## 📚 Documentation

- **[Deployment Guide](SAAS_DEPLOYMENT_GUIDE.md)** - Complete deployment instructions
- **[Architecture Summary](SAAS_ARCHITECTURE_SUMMARY.md)** - Technical architecture details
- **[API Documentation](http://localhost:8000/docs)** - FastAPI auto-generated docs

---

## 🐛 Troubleshooting

### Database Connection Error
```bash
# Check PostgreSQL is running
pg_isready

# Test connection
psql -U salla_user -d salla_optimizer
```

### Redis Connection Error
```bash
# Check Redis is running
redis-cli ping

# Should return: PONG
```

### Celery Tasks Not Running
```bash
# Check Celery worker is running
celery -A scheduler.celery_app inspect active

# Check Celery beat is running
celery -A scheduler.celery_app inspect scheduled
```

### OAuth Errors
```bash
# Check callback URL matches
echo $OAUTH_CALLBACK_URL

# Check Salla app configuration
# Verify redirect URL in Salla Partner Dashboard
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🙏 Acknowledgments

- **Salla** - E-commerce platform
- **CrewAI** - Multi-agent framework
- **FastAPI** - Modern web framework
- **Celery** - Distributed task queue

---

## 📞 Support

- **Documentation**: See docs/ folder
- **Issues**: GitHub Issues
- **Email**: support@yourcompany.com

---

## 🎯 Roadmap

### Phase 1 (Current)
- [x] Multi-tenant architecture
- [x] OAuth integration
- [x] Background automation
- [x] Database schema
- [x] Docker deployment

### Phase 2 (Next)
- [ ] User dashboard
- [ ] Email notifications
- [ ] Billing system (Stripe)
- [ ] Advanced analytics
- [ ] Mobile app

### Phase 3 (Future)
- [ ] White label solution
- [ ] API marketplace
- [ ] Machine learning models
- [ ] Multi-language support
- [ ] Enterprise features

---

**🎉 Ready to transform your Salla store pricing!**

Start onboarding stores today and let AI handle the rest.
