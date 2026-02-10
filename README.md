# 🛍️ Salla Price Optimizer - Multi-Tenant SaaS Platform

**AI-Powered Dynamic Pricing System for Salla E-commerce Stores**

[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11-green)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)](https://streamlit.io/)

---

## 🚀 Quick Start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running
- API Keys: OpenAI, Tavily, Salla OAuth tokens

### Start the System

**Windows:**
```bash
scripts\START_DOCKER.bat
```

**Linux/Mac:**
```bash
docker-compose up -d
```

### Access Services

| Service | URL | Description |
|---------|-----|-------------|
| 🛍️ Dashboard | http://localhost:8501 | Multi-tenant SaaS dashboard |
| 🔐 API | http://localhost:8000 | OAuth & REST API |
| 🌸 Flower | http://localhost:5555 | Celery task monitor |
| 📊 API Docs | http://localhost:8000/docs | Interactive API documentation |

---

## 📦 System Architecture

### 7 Docker Containers

1. **PostgreSQL** - Multi-tenant database
2. **Redis** - Message broker & cache
3. **FastAPI** - OAuth handler & REST API
4. **Celery Worker** - Background job processor
5. **Celery Beat** - Task scheduler
6. **Flower** - Task monitoring UI
7. **Streamlit** - Professional SaaS dashboard

### 6 Automated Tasks

- **optimize_store** - Single store optimization
- **optimize_all_stores** - Batch optimization (every 6 hours)
- **check_and_optimize_stores** - Smart scheduling (hourly)
- **refresh_expired_tokens** - Token management (daily)
- **cleanup_old_data** - Database maintenance (weekly)
- **manual_optimize** - On-demand optimization

---

## 🎯 Key Features

### Multi-Tenant Architecture
✅ Unlimited stores per instance  
✅ Complete data isolation  
✅ Per-store settings & automation  
✅ OAuth2 onboarding flow

### AI-Powered Pricing
✅ GPT-4 strategic analysis  
✅ Market intelligence (Tavily)  
✅ Competitor price tracking  
✅ Risk-based decision making  
✅ Profit margin protection

### Professional Dashboard
✅ Multi-store selector  
✅ Real-time analytics  
✅ AI price suggestions  
✅ Approve/reject workflow  
✅ Live task monitoring  
✅ Activity logs

### Automation Modes
- **Manual:** You approve all changes
- **Semi-Auto:** Low-risk auto-approved
- **Full-Auto:** Fully autonomous

---

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Required
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
SALLA_ACCESS_TOKEN=ory_at_...
SALLA_REFRESH_TOKEN=ory_rt_...

# Optional
SALLA_CLIENT_ID=
SALLA_CLIENT_SECRET=
DB_PASSWORD=salla_secure_password_2024
LOG_LEVEL=INFO
```

---

## 📊 Project Structure

```
salla-price-optimizer/
├── agents/              # AI agents (Scout, Analysis, Executor)
├── api/                 # FastAPI OAuth handler
├── database/            # SQLAlchemy models & schema
├── optimizer/           # Multi-tenant optimizer
├── scheduler/           # Celery tasks & config
├── tools/               # Market search & vision tools
├── scripts/             # Helper scripts & utilities
├── tests/               # Test files
├── docs/                # Documentation archive
├── dashboard_saas.py    # Streamlit dashboard
├── main.py              # Single-store entry point
├── docker-compose.yml   # Docker orchestration
├── Dockerfile           # Container image
└── requirements_saas.txt # Python dependencies
```

---

## 🛠️ Troubleshooting

### Containers Not Starting?

```bash
# Run diagnostics
scripts\diagnose.bat

# View logs
scripts\check_logs.bat

# Force rebuild
scripts\rebuild.bat
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Port conflicts | Run diagnostics script |
| Line ending errors | Run `scripts\fix_line_endings.bat` |
| Database connection failed | `docker-compose down -v && docker-compose up -d` |
| Containers exit immediately | Check logs with diagnostics script |

---

## 🗄️ Database Schema

7 tables for complete multi-tenant management:

1. **stores** - Store credentials & settings
2. **products** - Product catalog per store
3. **competitors** - Competitor pricing data
4. **pricing_decisions** - Audit trail of price changes
5. **optimization_runs** - History of optimization jobs
6. **activity_logs** - System events & user actions
7. **system_settings** - Global configuration

---

## 🔄 Workflow

### Store Onboarding
```
User → OAuth (Port 8000) → Database → Store Created
```

### Automated Optimization
```
Celery Beat → Celery Worker → Multi-Tenant Optimizer
↓
Scout Agent (Discover Products) → Tavily Search
↓
Analysis Agent (AI Pricing) → OpenAI GPT-4
↓
Executor Agent (Update Prices) → Salla API
↓
Database (Save Results)
```

### Dashboard View
```
User → Dashboard (Port 8501) → Database → Display Results
```

---

## 🔐 Security

- ✅ OAuth2 authentication
- ✅ Token auto-refresh
- ✅ Per-store data isolation
- ✅ API key protection
- ✅ Docker network isolation
- ✅ Environment variable encryption

---

## 📈 Monitoring

### Flower (Celery Monitor)
- URL: http://localhost:5555
- Username: `admin`
- Password: `admin123`

### Health Checks
```bash
# API
curl http://localhost:8000/health

# Database
docker-compose exec db pg_isready -U salla_user

# Redis
docker-compose exec redis redis-cli ping
```

---

## 📚 Documentation

Additional documentation available in `docs/archive/`:
- System Architecture
- Deployment Guides
- Troubleshooting
- API References
- Arabic Documentation

---

## ✅ Success Criteria

System is working when:

- ✅ All 7 containers running in Docker Desktop
- ✅ Dashboard accessible at http://localhost:8501
- ✅ API responds at http://localhost:8000/health
- ✅ Database has 7 tables
- ✅ Celery worker processing tasks
- ✅ No errors in logs

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License.

---

**Built with ❤️ for Salla merchants**

*Automate your pricing, maximize your profits*
