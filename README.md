# 🛍️ Salla Price Optimizer - Multi-Tenant SaaS Platform

**AI-Powered Dynamic Pricing System for Salla Stores**

[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11-green)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)](https://streamlit.io/)

---

## 🚀 Quick Start

### 1. Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running
- API Keys:
  - OpenAI API Key
  - Tavily API Key
  - Salla Access Token & Refresh Token

### 2. Start the System

**Windows:**
```bash
START_DOCKER.bat
```

**Linux/Mac:**
```bash
docker-compose up -d
```

### 3. Access Services

| Service | URL | Description |
|---------|-----|-------------|
| 🛍️ Dashboard | http://localhost:8501 | Multi-tenant SaaS dashboard |
| 🔐 API | http://localhost:8000 | OAuth & REST API |
| 🌸 Flower | http://localhost:5555 | Celery task monitor |
| 📊 API Docs | http://localhost:8000/docs | Interactive API documentation |

---

## 📦 What's Included

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

## 🎯 Features

### Multi-Tenant Architecture
- ✅ Unlimited stores per instance
- ✅ Complete data isolation
- ✅ Per-store settings & automation
- ✅ OAuth2 onboarding flow

### AI-Powered Pricing
- ✅ GPT-4 strategic analysis
- ✅ Market intelligence (Tavily)
- ✅ Competitor price tracking
- ✅ Risk-based decision making
- ✅ Profit margin protection

### Professional Dashboard
- ✅ Multi-store selector
- ✅ Real-time analytics
- ✅ AI price suggestions
- ✅ Approve/reject workflow
- ✅ Live task monitoring
- ✅ Activity logs

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

### Store Settings

Configure per store in dashboard:
- Minimum profit margin (%)
- Automation mode (manual/semi-auto/full-auto)
- Update frequency (hours)
- Risk tolerance (low/medium/high)

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  SALLA PRICE OPTIMIZER SAAS                 │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   DASHBOARD      │────▶│   FASTAPI API    │────▶│   POSTGRESQL     │
│  (Streamlit)     │     │  (OAuth/REST)    │     │   (Database)     │
│  Port: 8501      │     │  Port: 8000      │     │   Port: 5432     │
└──────────────────┘     └──────────────────┘     └──────────────────┘
         │                        │                         │
         └────────────────────────┼─────────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │        REDIS              │
                    │   (Message Broker)        │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │    CELERY WORKER          │
                    │  (Background Jobs)        │
                    └───────────────────────────┘
```

---

## 🛠️ Troubleshooting

### Containers Not Showing?

**Run diagnostics:**
```bash
diagnose.bat
```

**View logs:**
```bash
check_logs.bat
```

**Force rebuild:**
```bash
rebuild.bat
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Port conflicts | Run `diagnose.bat` to check ports |
| Line ending errors | Run `fix_line_endings.bat` |
| Database connection failed | Run `docker-compose down -v && docker-compose up -d` |
| Containers exit immediately | Check logs with `check_logs.bat` |

**Full troubleshooting guide:** See `TROUBLESHOOTING.md`

---

## 📚 Documentation

| File | Description |
|------|-------------|
| `START_HERE.md` | Quick start guide |
| `TROUBLESHOOTING.md` | Comprehensive troubleshooting |
| `README_AR.md` | Arabic documentation |
| `SYSTEM_STATUS.md` | Architecture overview |
| `DEPLOYMENT_CHECKLIST.md` | Deployment verification |
| `FIXES_APPLIED.md` | Recent fixes & improvements |

---

## 🔄 Workflow

### 1. Store Onboarding
```
User → OAuth (Port 8000) → Database → Store Created
```

### 2. Automated Optimization
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

### 3. Manual Optimization
```
User clicks "Run Now" → Celery Task → Same flow as above
```

### 4. Dashboard View
```
User → Dashboard (Port 8501) → Database → Display Results
```

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

## 🚀 Deployment

### Development
```bash
START_DOCKER.bat
```

### Production

1. **Update environment variables:**
   ```bash
   OAUTH_CALLBACK_URL=https://yourdomain.com/oauth/callback
   LOG_LEVEL=WARNING
   ```

2. **Use managed services:**
   - PostgreSQL: AWS RDS, Azure Database
   - Redis: AWS ElastiCache, Azure Cache

3. **Add reverse proxy:**
   - nginx or Traefik
   - HTTPS with Let's Encrypt

4. **Enable monitoring:**
   - Sentry for error tracking
   - Prometheus + Grafana for metrics

**Full deployment guide:** See `DEPLOYMENT_CHECKLIST.md`

---

## 🔐 Security

- ✅ OAuth2 authentication
- ✅ Token auto-refresh
- ✅ Per-store data isolation
- ✅ API key protection
- ✅ Docker network isolation
- ✅ Environment variable encryption

**Production recommendations:**
- Change default passwords
- Enable HTTPS
- Restrict Flower access
- Use managed databases
- Enable firewall rules

---

## 📈 Monitoring

### Flower (Celery Monitor)
- URL: http://localhost:5555
- Username: `admin`
- Password: `admin123`

### Docker Desktop
- View resource usage
- Container logs
- Performance metrics

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

## 🛠️ Development

### Project Structure
```
salla-price-optimizer/
├── agents/              # AI agents (Scout, Analysis, Executor)
├── api/                 # FastAPI OAuth handler
├── database/            # SQLAlchemy models & schema
├── optimizer/           # Multi-tenant optimizer
├── scheduler/           # Celery tasks & config
├── tools/               # Market search & vision tools
├── dashboard_saas.py    # Streamlit dashboard
├── docker-compose.yml   # Docker orchestration
├── Dockerfile           # Container image
├── requirements_saas.txt # Python dependencies
└── .env                 # Environment variables
```

### Running Tests
```bash
docker-compose exec web pytest
```

### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f celery_worker
```

### Database Access
```bash
docker-compose exec db psql -U salla_user -d salla_optimizer
```

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

## 🆘 Support

### Quick Help
1. Run `diagnose.bat` for system diagnostics
2. Check `TROUBLESHOOTING.md` for solutions
3. View logs with `check_logs.bat`
4. Try `rebuild.bat` for fresh start

### Documentation
- **English:** `START_HERE.md`, `TROUBLESHOOTING.md`
- **Arabic:** `README_AR.md`

### Issues
- Check existing issues on GitHub
- Create new issue with diagnostic output
- Include logs from `check_logs.bat`

---

## 🎉 Success Criteria

System is working when:

- ✅ All 7 containers running in Docker Desktop
- ✅ Dashboard accessible at http://localhost:8501
- ✅ API responds at http://localhost:8000/health
- ✅ Database has 7 tables
- ✅ Celery worker processing tasks
- ✅ No errors in logs

---

## 📞 Contact

- **GitHub:** [Your GitHub Profile]
- **Email:** [Your Email]
- **Documentation:** See `docs/` folder

---

**Built with ❤️ for Salla merchants**

*Automate your pricing, maximize your profits*
