# AI Fraud Risk Detection - Backend API

FastAPI + PostgreSQL backend for the AI-powered Fraud & Risk Detection Platform.

## Features

- **Authentication & RBAC**: JWT-based auth with Admin, Business Manager, Analyst roles
- **Transaction Management**: CRUD, CSV import, API ingestion, search & filtering
- **AI Risk Scoring**: Isolation Forest ML model + configurable business rules (0-100 score)
- **AI Explanations**: Google Gemini integration for human-readable risk explanations
- **Fraud Alerts**: Auto-generated alerts with severity, status workflow
- **Investigation System**: Transaction detail, customer profiles, related entities
- **Dashboard API**: KPIs, trends, risk distribution, suspicious entities
- **Network Graph**: Fraud network visualization data (Customer→Device→IP→Transaction→Location)
- **Reports**: CSV/PDF export for daily/monthly fraud, high-risk customers, confirmed fraud
- **Rules Engine**: Configurable business rules managed via API
- **Feedback Loop**: Confirmed fraud / false positive tracking for model improvement
- **Real-time**: WebSocket support for live dashboard updates

## Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 15+
- Redis 7+ (optional, for Celery)

### Local Development

1. **Clone and setup**
```bash
cd backend
cp .env.example .env
# Edit .env with your settings
```

2. **Start dependencies**
```bash
docker-compose up -d postgres redis
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run migrations**
```bash
alembic upgrade head
```

5. **Seed database**
```bash
python seed_data.py
```

6. **Start server**
```bash
uvicorn app.main:app --reload
```

7. **Access API docs**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Docker
```bash
docker-compose up --build
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login, get JWT |
| GET | `/api/v1/auth/me` | Current user profile |
| GET | `/api/v1/auth/users` | List users (admin) |

### Transactions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/transactions` | Submit transaction |
| POST | `/api/v1/transactions/batch` | Batch submit |
| GET | `/api/v1/transactions` | List with filters |
| GET | `/api/v1/transactions/search?q=` | Search |
| GET | `/api/v1/transactions/{id}` | Get detail |
| POST | `/api/v1/transactions/import/csv` | CSV import |

### Risk Scoring
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/risk/score` | Score single transaction |
| POST | `/api/v1/risk/batch` | Score multiple |
| GET | `/api/v1/risk/flags` | List risk flags |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/dashboard/stats` | All dashboard data |
| GET | `/api/v1/dashboard/trends` | Transaction trends |
| GET | `/api/v1/dashboard/risk-distribution` | Risk levels |
| GET | `/api/v1/dashboard/suspicious-customers` | Top risky customers |
| GET | `/api/v1/dashboard/suspicious-devices` | Top risky devices |
| GET | `/api/v1/dashboard/alerts` | Recent alerts |

### Network Graph
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/network/graph` | Graph data |
| GET | `/api/v1/network/clusters` | Suspicious clusters |

### Investigation
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/investigation/transaction/{id}` | Full investigation |
| GET | `/api/v1/investigation/customer/{id}/profile` | Customer profile |
| POST | `/api/v1/investigation/transaction/{id}/notes` | Add notes |
| POST | `/api/v1/investigation/question` | Ask AI assistant |

### Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/reports/generate` | Generate report |
| POST | `/api/v1/reports/generate/stream` | Stream report |
| GET | `/api/v1/reports/templates` | Available templates |

### Rules Engine
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/rules` | List rules |
| POST | `/api/v1/rules` | Create rule |
| PATCH | `/api/v1/rules/{id}` | Update rule |
| DELETE | `/api/v1/rules/{id}` | Delete rule |
| POST | `/api/v1/rules/test` | Test rules |

### Alerts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/alerts` | List alerts |
| GET | `/api/v1/alerts/{id}` | Get alert |
| PATCH | `/api/v1/alerts/{id}` | Update alert |
| POST | `/api/v1/alerts/{id}/assign` | Assign alert |

### Feedback
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/feedback` | Submit feedback |
| GET | `/api/v1/feedback/transaction/{id}` | Get feedback |

## Default Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@fraud.com | admin123 |
| Manager | manager@fraud.com | manager123 |
| Analyst | analyst@fraud.com | analyst123 |

## ML Model Training

```bash
cd ml_engine
# Place transactions.csv in this directory
python preprocess.py
python train.py
# Model artifacts saved to saved_models/
```

## Project Structure

```
backend/
├── app/
│   ├── core/           # Config, database, security, exceptions
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── routers/        # API endpoints
│   ├── services/       # Business logic
│   └── main.py         # FastAPI app
├── ml_engine/          # ML model (Isolation Forest)
├── alembic/            # Database migrations
├── seed_data.py        # Database seeding
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Environment Variables

See `.env.example` for all configuration options.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key (32+ chars)
- `GEMINI_API_KEY`: Google Gemini API key for AI explanations
- `BACKEND_CORS_ORIGINS`: Allowed frontend origins

## Testing

```bash
pytest tests/ -v --cov=app
```

## License

Internal use only.