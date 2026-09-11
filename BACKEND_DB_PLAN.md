# Backend & DB Lead - Development Plan
## AI Fraud & Risk Detection Platform

---

## 1. Current Codebase Analysis

### What Already Exists (Other Branches)

| Branch | Owner | What Was Built | Status |
|--------|-------|----------------|--------|
| `main` | Team | `frontend-dashboard/` (React + Vite + Tailwind, mock data), `ml_engine/` (structure) | Frontend mock done |
| `M-Faizan-Ashraf` | Faizan | `ml_engine/` - `risk_engine.py`, `predict.py`, `preprocess.py`, `train.py` (Isolation Forest + business rules) | ML pipeline done |
| `M-Awais` | Awais (You) | `ai_logic.py` - Gemini API integration, fraud rules engine, AI explanations | AI logic done |
| `nimra` | Nimra | README only | Pending (Frontend UI/UX) |
| `Mina-Khan` | Mina | README only | Pending (Frontend API Integrator) |
| `Ahmad-Abbaas` | Ahmad | README only | Pending (Network Graph & QA) |

### Key Integration Points

- **ML Engine** (`M-Faizan-Ashraf`): Exposes `generate_final_decision(transaction)` returning `{transaction_id, ml_anomaly_score, rule_engine_score, final_risk_score, risk_level, decision, risk_flags}`
- **AI Logic** (`M-Awais`): Uses Gemini API to generate human-readable fraud explanations from risk flags
- **Frontend Dashboard** (`main`): React app with mock KPI cards, charts, alerts - currently all local data

---

## 2. Backend Scope - What You Need to Build

### 2.1 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Settings, env vars, DB URL
│   ├── database.py              # SQLAlchemy engine + session
│   ├── models/
│   │   ├── __init__.py
│   │   ├── transaction.py       # Transaction ORM model
│   │   ├── user.py              # User/Analyst ORM model
│   │   └── alert.py             # Fraud alert ORM model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── transaction.py       # Pydantic request/response schemas
│   │   ├── risk.py              # Risk score response schema
│   │   └── auth.py              # Auth schemas (login/register)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── transactions.py      # /api/transactions endpoints
│   │   ├── risk.py              # /api/risk endpoints
│   │   ├── dashboard.py         # /api/dashboard endpoints
│   │   └── auth.py              # /api/auth endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ml_integration.py    # Calls ml_engine.risk_engine
│   │   ├── ai_integration.py    # Calls ai_logic for explanations
│   │   └── dashboard_stats.py   # Aggregation queries for dashboard
│   └── middleware/
│       ├── __init__.py
│       └── cors.py              # CORS configuration
├── alembic/                     # DB migrations
│   ├── alembic.ini
│   └── versions/
├── seed_data.py                 # Insert sample transactions
├── requirements.txt
├── .env.example
└── Dockerfile
```

### 2.2 Tech Stack

- **Framework**: FastAPI 0.115+
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Auth**: JWT (python-jose + passlib)
- **Driver**: asyncpg

### 2.3 API Endpoints

#### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register analyst account |
| POST | `/api/auth/login` | Login, returns JWT |
| GET | `/api/auth/me` | Get current user profile |

#### Transactions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/transactions` | List all transactions (paginated, filterable) |
| GET | `/api/transactions/{id}` | Get single transaction detail |
| POST | `/api/transactions` | Submit new transaction for analysis |
| GET | `/api/transactions/{id}/risk` | Get full risk analysis for a transaction |
| GET | `/api/transactions/search` | Search by ID, customer, amount range |

#### Risk Analysis
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/risk/score` | Score a single transaction (ML + rules) |
| POST | `/api/risk/batch` | Score multiple transactions |
| GET | `/api/risk/flags` | List all triggered risk flags |

#### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/stats` | KPI cards data (total txns, high-risk count, avg score) |
| GET | `/api/dashboard/trends` | Transaction + risk trend data (for charts) |
| GET | `/api/dashboard/risk-distribution` | Risk level distribution (low/medium/high) |
| GET | `/api/dashboard/alerts` | Recent fraud alerts |
| GET | `/api/dashboard/suspicious-customers` | Top flagged customers |
| GET | `/api/dashboard/suspicious-devices` | Flagged devices/IPs |

### 2.4 Database Schema

#### `transactions` table
```sql
CREATE TABLE transactions (
    id              SERIAL PRIMARY KEY,
    transaction_id  VARCHAR(50) UNIQUE NOT NULL,
    user_id         INTEGER REFERENCES users(id),
    amount          DECIMAL(12,2) NOT NULL,
    currency        VARCHAR(3) DEFAULT 'USD',
    country         VARCHAR(100),
    bin_country     VARCHAR(100),
    channel         VARCHAR(50),          -- web, mobile, api
    merchant_category VARCHAR(100),
    promo_used      BOOLEAN DEFAULT FALSE,
    avs_match       BOOLEAN DEFAULT TRUE,
    cvv_result      BOOLEAN DEFAULT TRUE,
    three_ds_flag   BOOLEAN DEFAULT FALSE,
    shipping_distance_km DECIMAL(8,2),
    account_age_days INTEGER,
    total_transactions_user INTEGER,
    avg_amount_user DECIMAL(12,2),
    is_fraud        BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT NOW()
);
```

#### `risk_assessments` table
```sql
CREATE TABLE risk_assessments (
    id              SERIAL PRIMARY KEY,
    transaction_id  VARCHAR(50) REFERENCES transactions(transaction_id),
    ml_anomaly_score    DECIMAL(5,2),
    rule_engine_score   DECIMAL(5,2),
    final_risk_score    DECIMAL(5,2),
    risk_level          VARCHAR(10),      -- LOW, MEDIUM, HIGH
    decision            VARCHAR(20),      -- APPROVE, REVIEW, BLOCK
    risk_flags          JSONB,
    ai_explanation      TEXT,
    assessed_at         TIMESTAMP DEFAULT NOW()
);
```

#### `alerts` table
```sql
CREATE TABLE alerts (
    id              SERIAL PRIMARY KEY,
    transaction_id  VARCHAR(50) REFERENCES transactions(transaction_id),
    severity        VARCHAR(10),          -- LOW, MEDIUM, HIGH, CRITICAL
    reason          TEXT,
    status          VARCHAR(20) DEFAULT 'OPEN',  -- OPEN, INVESTIGATING, RESOLVED, FALSE_POSITIVE
    assigned_to     INTEGER REFERENCES users(id),
    created_at      TIMESTAMP DEFAULT NOW(),
    resolved_at     TIMESTAMP
);
```

#### `users` table
```sql
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255),
    role            VARCHAR(20) DEFAULT 'analyst',  -- analyst, admin
    created_at      TIMESTAMP DEFAULT NOW()
);
```

---

## 3. Integration Plan with Existing Code

### 3.1 ML Engine Integration

The `M-Faizan-Ashraf` branch already has `risk_engine.py` with `generate_final_decision()`. Your backend will:

1. Copy/recreate the `ml_engine/` folder into the backend project root
2. Import and call it in `services/ml_integration.py`:

```python
from ml_engine.risk_engine import generate_final_decision

def score_transaction(transaction_data: dict) -> dict:
    return generate_final_decision(transaction_data)
```

3. Store the result in `risk_assessments` table
4. If the ML model artifacts (`saved_models/`) are not present, handle gracefully with fallback to rule-only scoring

### 3.2 AI Logic Integration

The `M-Awais` branch has `ai_logic.py` with Gemini API. Your backend will:

1. Refactor into `services/ai_integration.py`
2. Move the Gemini API key to `.env`
3. Accept risk flags and return AI explanation:

```python
from google import genai
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_ai_explanation(risk_flags: list) -> str:
    prompt = f"""
    You are a fraud analyst expert.
    A transaction was flagged for these reasons: {risk_flags}.
    Explain why this is high risk in 2 short bullet points.
    """
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt
    )
    return response.text
```

4. Store the explanation in `risk_assessments.ai_explanation`

### 3.3 Frontend Integration

The `Mina-Khan` branch (Frontend API Integrator) will connect to your backend. You need to:

1. Enable CORS for `http://localhost:5173` (Vite dev server)
2. Ensure all dashboard endpoints return the exact shape the frontend expects
3. Document the API contract so the frontend integrator can code against it

---

## 4. Development Phases

### Phase 1: Foundation (Days 1-2)
- [ ] Set up FastAPI project structure
- [ ] Configure PostgreSQL connection + SQLAlchemy
- [ ] Create `.env` with DB credentials, Gemini API key
- [ ] Write all ORM models
- [ ] Run Alembic migrations
- [ ] Create basic health check endpoint (`GET /api/health`)

### Phase 2: Auth (Day 3)
- [ ] User registration + login with JWT
- [ ] Password hashing with passlib/bcrypt
- [ ] Middleware for protected routes
- [ ] Test auth flow with Postman/curl

### Phase 3: Transaction CRUD (Days 4-5)
- [ ] `POST /api/transactions` - submit new transaction
- [ ] `GET /api/transactions` - list with pagination + filters
- [ ] `GET /api/transactions/{id}` - single transaction detail
- [ ] `GET /api/transactions/search` - search by ID, customer, amount

### Phase 4: Risk Engine Integration (Days 6-7)
- [ ] Copy `ml_engine/` into backend project
- [ ] Build `services/ml_integration.py` wrapping `generate_final_decision()`
- [ ] Build `services/ai_integration.py` wrapping Gemini explanation
- [ ] `POST /api/risk/score` - score a single transaction
- [ ] `POST /api/risk/batch` - score multiple transactions
- [ ] Store results in `risk_assessments` table
- [ ] Auto-generate alerts for HIGH risk transactions

### Phase 5: Dashboard API (Days 8-9)
- [ ] `GET /api/dashboard/stats` - KPI aggregation queries
- [ ] `GET /api/dashboard/trends` - time-series data
- [ ] `GET /api/dashboard/risk-distribution` - risk level counts
- [ ] `GET /api/dashboard/alerts` - recent alerts list
- [ ] `GET /api/dashboard/suspicious-customers` - top flagged users
- [ ] `GET /api/dashboard/suspicious-devices` - flagged devices/IPs

### Phase 6: Seed Data & Testing (Day 10)
- [ ] Write `seed_data.py` to insert 100-500 sample transactions
- [ ] Test all endpoints with different data scenarios
- [ ] Verify ML scoring works end-to-end
- [ ] Verify AI explanations are generated
- [ ] Performance test dashboard aggregation queries

---

## 5. API Response Contracts

### Dashboard Stats Response
```json
{
  "total_transactions": 15420,
  "high_risk_count": 234,
  "medium_risk_count": 891,
  "low_risk_count": 14295,
  "confirmed_fraud": 45,
  "false_positives": 12,
  "open_alerts": 18,
  "avg_risk_score": 23.5
}
```

### Transaction List Response
```json
{
  "transactions": [
    {
      "id": 1,
      "transaction_id": "TXN-998877",
      "amount": 1200.00,
      "country": "US",
      "channel": "web",
      "merchant_category": "electronics",
      "risk_level": "HIGH",
      "risk_score": 78.5,
      "decision": "REVIEW",
      "created_at": "2026-09-10T14:30:00"
    }
  ],
  "total": 15420,
  "page": 1,
  "per_page": 20
}
```

### Risk Score Response
```json
{
  "transaction_id": "TXN-998877",
  "ml_anomaly_score": 72.3,
  "rule_engine_score": 85.0,
  "final_risk_score": 78.5,
  "risk_level": "HIGH",
  "decision": "REVIEW",
  "risk_flags": [
    "High transaction amount (>$1000)",
    "New account high-value transaction"
  ],
  "ai_explanation": "This transaction is high risk because the amount is significantly above the user's typical spending pattern, and the account is less than 14 days old."
}
```

---

## 6. Dependencies (requirements.txt)

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy[asyncio]==2.0.35
asyncpg==0.30.0
alembic==1.14.0
pydantic==2.10.0
pydantic-settings==2.6.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.1
pandas==2.2.0
numpy==2.0.0
scikit-learn==1.5.0
joblib==1.4.0
google-genai==1.0.0
httpx==0.28.0
```

---

## 7. Key Considerations

1. **Environment Variables** - Never commit `.env`. Use `.env.example` as template.
2. **CORS** - Allow `http://localhost:5173` for frontend dev.
3. **Error Handling** - Return consistent `{ "detail": "error message" }` format.
4. **Pagination** - All list endpoints support `?page=1&per_page=20`.
5. **ML Model Fallback** - If `saved_models/` not present, use rule-only scoring with a warning.
6. **Database Indexes** - Add indexes on `transaction_id`, `risk_level`, `created_at` for query performance.
7. **Async SQLAlchemy** - Use async engine for non-blocking DB operations under load.

---

## 8. Coordination with Team

| Teammate | What They Need From You | What You Need From Them |
|----------|------------------------|------------------------|
| **Faizan (ML)** | Confirm `generate_final_decision()` input/output contract | `ml_engine/` code and model artifacts |
| **Awais (AI Logic)** | Refactor `ai_logic.py` into a callable service function | Gemini API key, prompt template |
| **Mina (Frontend API)** | API base URL, endpoint docs, response JSON shapes | Connect dashboard to your endpoints |
| **Nimra (Frontend UI)** | Mock API responses or local JSON to build UI before backend is ready | Dashboard component designs |
| **Ahmad (Network/QA)** | Running backend to test, test transaction data | Test coverage for API endpoints |

---

*Plan prepared for Backend & DB Lead role - FastAPI + PostgreSQL*
*Project: AI Fraud & Risk Detection Platform*
