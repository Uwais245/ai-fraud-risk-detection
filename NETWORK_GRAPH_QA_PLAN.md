# Network Graph & QA - Development Plan
## AI Fraud & Risk Detection Platform

**Role**: Network Graph & QA (Visualizations & System Testing)  
**Branch**: `Ahmad-Abbaas`  
**Branch Owner**: Ahmad-Abbaas (You)

---

## 1. Scope from PDF Requirements

Based on the project specification (PDF), your responsibilities cover:

| PDF Section | Requirement | Your Deliverable |
|-------------|-------------|------------------|
| **12. Fraud Network Detection** | Visual relationship view: Customer → Device → IP → Transaction → Location | Interactive network graph component |
| **13. Dashboard** | Charts: fraud trends, risk distribution, suspicious customers/devices/IPs | Chart components (Recharts/D3) |
| **16. Reports** | Export capabilities | Export to CSV/PDF functionality |
| **18. Real-Time Detection** | Dashboard should reflect real-time updates | WebSocket integration for live updates |
| **19. Technology** | React/Next.js, Charts, Investigation interface, Fraud network visualization | Frontend implementation |
| **QA/Testing** | System testing, quality assurance | Test suite, CI/CD integration |

---

## 2. Current State Analysis

### What Already Exists (Other Branches)

| Branch | Owner | What Was Built | Status |
|--------|-------|----------------|--------|
| `main` | Team | `frontend-dashboard/` (React + Vite + Tailwind, **mock data only**), `ml_engine/` | Frontend skeleton done |
| `M-Faizan-Ashraf` | Faizan | `ml_engine/` - complete ML pipeline (Isolation Forest + rules) | ML done |
| `M-Awais` | Awais | `ai_logic.py` - Gemini API, fraud rules, AI explanations | AI logic done |
| `nimra` | Nimra | README only | Pending (UI/UX) |
| `Mina-Khan` | Mina | README only | Pending (API Integration) |
| `Ahmad-Abbaas` | **You** | README only | **Your task starts here** |

### Key Integration Points

- **Backend API** (to be built by Backend Lead): Will expose `/api/dashboard/*` endpoints
- **ML Engine** (`M-Faizan-Ashraf`): Returns risk scores with `risk_flags` array
- **AI Logic** (`M-Awais`): Returns human-readable explanations from risk flags
- **Frontend Dashboard** (`main`): Has mock KPI cards, charts, alerts - needs real API + network graph

---

## 3. What You Need to Build

### 3.1 Fraud Network Visualization (Core Feature - PDF Section 12)

**Requirement**: Interactive graph showing connections between:
```
Customer → Device → IP → Transaction → Location
```

**Example from PDF**:
```
Customer A ── Device X ── IP 192.168.X.X
                     │
Customer B ─────────┘
                     │
Customer C ── Device X
```

**Technical Approach**:
- Use **D3.js** or **Cytoscape.js** for force-directed graph
- Or **React Flow** for more React-native approach
- Nodes: Customer, Device, IP, Transaction, Location
- Edges: Relationships (uses_device, uses_ip, made_transaction, from_location)
- Features: Zoom, pan, click node for details, filter by risk level, highlight suspicious clusters

**Data Source**: Backend API endpoint `/api/network/graph?customer_id=X&depth=2`

### 3.2 Dashboard Charts (PDF Section 13)

Extend the existing `frontend-dashboard` with real data from backend:

| Chart | Backend Endpoint | Library |
|-------|------------------|---------|
| Transaction Volume Trend | `/api/dashboard/trends` | Recharts (LineChart) |
| Risk Distribution (Low/Med/High) | `/api/dashboard/risk-distribution` | Recharts (PieChart/BarChart) |
| Fraud Alerts Timeline | `/api/dashboard/alerts` | Recharts (AreaChart) |
| Top Suspicious Customers | `/api/dashboard/suspicious-customers` | Table + BarChart |
| Top Suspicious Devices/IPs | `/api/dashboard/suspicious-devices` | Table + Network mini-graph |

### 3.3 Investigation Interface (PDF Section 10)

**Transaction Detail View** with:
- Customer information
- Transaction history (table)
- Related transactions (same device/IP/customer)
- Devices used (with risk indicators)
- IP addresses (with geo-location)
- Locations (map view)
- Risk factors (from `risk_flags`)
- AI explanation (from AI logic)
- Related alerts
- Investigation notes (CRUD)

### 3.4 Reports & Export (PDF Section 16)

- Daily/Monthly fraud activity reports
- High-risk customers/transactions reports
- Confirmed fraud / False positives reports
- Export to **CSV** and **PDF** (using `jspdf` or `pdfmake`)

### 3.5 Real-Time Updates (PDF Section 18)

- WebSocket connection to backend for live:
  - New high-risk transactions
  - Alert status changes
  - Risk score updates
- Dashboard auto-refresh without full reload

### 3.6 QA / Testing

| Test Type | Tools | Coverage |
|-----------|-------|----------|
| Unit Tests | Vitest + React Testing Library | Components, utils, hooks |
| Integration Tests | Vitest + MSW | API integration, data flow |
| E2E Tests | Playwright | Critical user flows |
| Visual Regression | Chromatic/Playwright | Chart/graph rendering |
| Performance | Lighthouse | Dashboard load time < 2s |

---

## 4. Frontend Architecture

### 4.1 Project Structure (Extending `main/frontend-dashboard`)

```
frontend-dashboard/
├── src/
│   ├── components/
│   │   ├── charts/              # Recharts wrappers
│   │   │   ├── RiskDistributionChart.jsx
│   │   │   ├── TransactionTrendChart.jsx
│   │   │   ├── AlertsTimelineChart.jsx
│   │   │   └── SuspiciousEntitiesChart.jsx
│   │   ├── network/
│   │   │   ├── FraudNetworkGraph.jsx      # Main D3/Cytoscape component
│   │   │   ├── NetworkNode.jsx
│   │   │   ├── NetworkEdge.jsx
│   │   │   ├── NetworkControls.jsx        # Zoom, filter, legend
│   │   │   └── NetworkTooltip.jsx
│   │   ├── dashboard/
│   │   │   ├── KPICard.jsx
│   │   │   ├── AlertsPanel.jsx
│   │   │   ├── SuspiciousCustomersTable.jsx
│   │   │   └── SuspiciousDevicesTable.jsx
│   │   ├── investigation/
│   │   │   ├── TransactionDetailModal.jsx
│   │   │   ├── CustomerProfilePanel.jsx
│   │   │   ├── RelatedTransactionsTable.jsx
│   │   │   ├── DevicesIPsPanel.jsx
│   │   │   ├── RiskFactorsPanel.jsx
│   │   │   ├── AIExplanationPanel.jsx
│   │   │   └── InvestigationNotes.jsx
│   │   ├── reports/
│   │   │   ├── ReportGenerator.jsx
│   │   │   ├── ExportButtons.jsx
│   │   │   └── ReportPreview.jsx
│   │   └── common/
│   │       ├── LoadingSpinner.jsx
│   │       ├── ErrorBoundary.jsx
│   │       └── DateRangePicker.jsx
│   ├── hooks/
│   │   ├── useDashboardData.js          # Fetch dashboard stats
│   │   ├── useNetworkGraph.js           # Fetch + transform network data
│   │   ├── useInvestigation.js          # Fetch transaction details
│   │   ├── useWebSocket.js              # Real-time updates
│   │   └── useReports.js                # Report generation
│   ├── services/
│   │   ├── api.js                       # Axios instance + interceptors
│   │   ├── dashboardApi.js              # Dashboard endpoints
│   │   ├── networkApi.js                # Network graph endpoints
│   │   ├── investigationApi.js          # Investigation endpoints
│   │   └── reportApi.js                 # Report endpoints
│   ├── utils/
│   │   ├── graphTransform.js            # Transform API data to graph format
│   │   ├── formatters.js                # Currency, date, risk level
│   │   └── exportUtils.js               # CSV/PDF export helpers
│   ├── context/
│   │   ├── AuthContext.jsx              # Auth state
│   │   └── WebSocketContext.jsx         # Real-time connection
│   ├── pages/
│   │   ├── Dashboard.jsx                # Main dashboard
│   │   ├── NetworkGraph.jsx             # Full-page network view
│   │   ├── Investigation.jsx            # Transaction investigation
│   │   ├── Reports.jsx                  # Reports page
│   │   └── Settings.jsx                 # User settings
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── package.json
├── vite.config.js
├── tailwind.config.js
└── playwright.config.js
```

### 4.2 Key Dependencies to Add

```json
{
  "dependencies": {
    "cytoscape": "^3.30.0",
    "cytoscape-cose-bilkent": "^4.1.0",
    "cytoscape-fcose": "^2.2.0",
    "recharts": "^2.12.0",
    "jspdf": "^2.5.0",
    "jspdf-autotable": "^3.8.0",
    "date-fns": "^3.6.0",
    "socket.io-client": "^4.7.0",
    "axios": "^1.7.0"
  },
  "devDependencies": {
    "vitest": "^2.0.0",
    "@testing-library/react": "^16.0.0",
    "playwright": "^1.45.0",
    "msw": "^2.3.0"
  }
}
```

---

## 5. Backend API Contract (What You Need from Backend Lead)

### 5.1 Network Graph Endpoints

```
GET /api/network/graph
Query: customer_id, transaction_id, device_id, ip_address, depth (default: 2), risk_level
Response:
{
  "nodes": [
    {"id": "cust-123", "type": "customer", "label": "CUST-123", "risk_level": "HIGH", "metadata": {...}},
    {"id": "dev-456", "type": "device", "label": "Device-X", "risk_level": "MEDIUM", "metadata": {...}},
    {"id": "ip-789", "type": "ip", "label": "192.168.1.1", "risk_level": "HIGH", "metadata": {...}}
  ],
  "edges": [
    {"source": "cust-123", "target": "dev-456", "type": "uses_device", "weight": 1},
    {"source": "dev-456", "target": "ip-789", "type": "uses_ip", "weight": 3}
  ]
}
```

```
GET /api/network/clusters
Query: min_cluster_size, risk_threshold
Response: Connected components with high-risk density
```

### 5.2 Dashboard Endpoints (Already in backend plan)

```
GET /api/dashboard/stats
GET /api/dashboard/trends?period=7d&interval=1d
GET /api/dashboard/risk-distribution
GET /api/dashboard/alerts?status=OPEN&limit=20
GET /api/dashboard/suspicious-customers?limit=10
GET /api/dashboard/suspicious-devices?limit=10
```

### 5.3 Investigation Endpoints

```
GET /api/investigation/transaction/{transaction_id}
Response: Full transaction + customer + risk assessment + AI explanation + related entities

GET /api/investigation/customer/{customer_id}/profile
Response: Customer risk profile (PDF Section 11)

GET /api/investigation/customer/{customer_id}/network
Response: Subgraph for this customer
```

### 5.4 Reports Endpoints

```
POST /api/reports/generate
Body: {type: "daily_fraud", period: "2026-09-10", format: "csv|pdf"}
Response: {download_url, expires_at}

GET /api/reports/templates
Response: Available report types
```

### 5.5 WebSocket Events

```
# Server → Client
"transaction:new_risk"      - New high-risk transaction
"alert:created"             - New alert
"alert:status_changed"      - Alert status update
"risk:recalculated"         - Risk score updated
```

---

## 6. Development Phases

### Phase 1: Setup & Network Graph Core (Days 1-3)
- [ ] Clone `main` branch, install dependencies
- [ ] Add Cytoscape/D3 + Recharts + testing deps
- [ ] Build `FraudNetworkGraph` component with mock data
- [ ] Implement node/edge rendering, zoom/pan, tooltips
- [ ] Add risk-level color coding (red/orange/green)
- [ ] Add filter controls (by node type, risk level, date range)

### Phase 2: Dashboard Charts & Real Data (Days 4-5)
- [ ] Replace mock data in `FraudDashboard.jsx` with API calls
- [ ] Build all chart components (RiskDistribution, TransactionTrend, etc.)
- [ ] Implement `useDashboardData` hook with caching
- [ ] Add date range picker for all charts
- [ ] Connect to backend `/api/dashboard/*` endpoints

### Phase 3: Investigation Interface (Days 6-7)
- [ ] Build `TransactionDetailModal` with tabs:
  - Overview (risk score, decision, AI explanation)
  - Customer Profile (PDF Section 11)
  - Related Transactions
  - Devices & IPs
  - Network View (mini graph)
  - Investigation Notes (CRUD)
- [ ] Implement `useInvestigation` hook

### Phase 4: Network Graph Advanced (Days 8-9)
- [ ] Connect to real `/api/network/graph` endpoint
- [ ] Add clustering/highlighting of suspicious groups
- [ ] Implement "Find path between two entities" feature
- [ ] Add export graph as image/JSON
- [ ] Performance optimization for large graphs (1000+ nodes)

### Phase 5: Reports & Export (Day 10)
- [ ] Build `ReportGenerator` component
- [ ] Implement CSV export for all tables
- [ ] Implement PDF export for reports (jspdf)
- [ ] Add scheduled report UI (optional)

### Phase 6: Real-Time & QA (Days 11-12)
- [ ] Implement WebSocket connection (`useWebSocket` hook)
- [ ] Add real-time updates to dashboard and network graph
- [ ] Write unit tests (target 70% coverage)
- [ ] Write integration tests for API hooks
- [ ] Write E2E tests for critical flows
- [ ] Set up CI/CD pipeline (GitHub Actions)

---

## 7. Coordination with Team

| Teammate | What You Need From Them | What They Need From You |
|----------|------------------------|------------------------|
| **Backend Lead** | All API endpoints above, WebSocket server, API docs (OpenAPI) | Network graph data requirements, expected response shapes |
| **Faizan (ML)** | Risk flags format, anomaly score interpretation | Visual encoding of ML risk scores in graph |
| **Awais (AI Logic)** | AI explanation format, prompt templates | How to display AI explanations in investigation view |
| **Nimra (UI/UX)** | Design system, color palette, component library | Network graph UX requirements, interaction patterns |
| **Mina (API Integrator)** | API integration layer, React Query/SWR setup | Endpoint contracts, error handling patterns |

---

## 8. Key Technical Decisions

### Network Graph Library: **Cytoscape.js**
- **Why**: Better performance for large graphs, built-in layouts (cose-bilkent, fcose), React wrapper available (`cytoscape-react` or custom)
- **Alternative**: D3.js (more control, steeper learning curve), React Flow (React-native but less graph-specific features)

### Chart Library: **Recharts** (already in `main` branch)
- Consistent with existing dashboard
- Good TypeScript support
- Composable React components

### State Management: **React Query (TanStack Query) + Context**
- Server state: React Query for caching, background refetch
- Client state: Context for auth, WebSocket, UI state

### Real-Time: **Socket.io Client**
- Backend should use Socket.io server
- Fallback to polling if WebSocket fails

---

## 9. Testing Strategy

### Unit Tests (Vitest)
```javascript
// Example: Network graph data transformation
test('transformAPIToGraph converts API response to Cytoscape elements', () => {
  const apiResponse = {nodes: [...], edges: [...]};
  const elements = transformAPIToGraph(apiResponse);
  expect(elements.nodes).toHaveLength(3);
  expect(elements.edges[0].data.source).toBe('cust-123');
});
```

### Integration Tests (MSW)
```javascript
// Mock API responses for dashboard hooks
test('useDashboardData fetches and caches stats', async () => {
  server.use(http.get('/api/dashboard/stats', () => HttpResponse.json(mockStats)));
  const {result} = renderHook(() => useDashboardData());
  await waitFor(() => expect(result.current.data).toEqual(mockStats));
});
```

### E2E Tests (Playwright)
```javascript
test('User can investigate a high-risk transaction', async ({page}) => {
  await page.goto('/dashboard');
  await page.click('[data-testid="high-risk-transaction"]');
  await expect(page.locator('[data-testid="investigation-modal"]')).toBeVisible();
  await expect(page.locator('[data-testid="ai-explanation"]')).toContainText('High Risk');
});
```

---

## 10. Definition of Done

- [ ] Network graph renders 500+ nodes at 60fps
- [ ] All dashboard charts show real data from backend
- [ ] Investigation view displays all PDF Section 10 requirements
- [ ] Reports generate and export to CSV/PDF
- [ ] Real-time updates work via WebSocket
- [ ] Unit test coverage > 70%
- [ ] E2E tests pass for 5 critical user flows
- [ ] Accessible (WCAG 2.1 AA) - keyboard nav, screen readers
- [ ] Responsive (works on 1366px+ and 1920px+)
- [ ] Documented in Storybook or component README

---

## 11. Risk & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Backend API not ready | High | High | Build with MSW mocks first, swap to real API later |
| Large graph performance | Medium | High | Implement virtualization, level-of-detail, clustering |
| WebSocket connection issues | Medium | Medium | Implement reconnection + polling fallback |
| Design changes from Nimra | Medium | Medium | Use design tokens, build flexible components |
| Integration conflicts with Mina | Medium | Medium | Define API contracts early, use OpenAPI spec |

---

*Plan for Network Graph & QA role (Ahmad-Abbaas branch)*  
*Based on PDF project specification - AI Fraud & Risk Detection Platform*