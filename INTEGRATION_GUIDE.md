# Frontend API Integration Layer

## Overview

This layer connects the React frontend to the FastAPI backend for the Fraud & Risk Detection Platform.

## Setup

1. Install dependencies:
   ```bash
   cd frontend-dashboard
   npm install
   ```

2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

3. Update `VITE_API_BASE_URL` in `.env` to match your backend URL.

4. Start the development server:
   ```bash
   npm run dev
   ```

## File Structure

```
src/
├── services/           # API service layer
│   ├── apiClient.js    # Base HTTP client with auth
│   ├── transactionService.js
│   ├── alertService.js
│   ├── dashboardService.js
│   ├── networkService.js
│   ├── riskService.js
│   └── index.js
│
├── hooks/              # Custom React hooks
│   ├── useTransactions.js
│   ├── useAlerts.js
│   ├── useDashboard.js
│   ├── useNetwork.js
│   ├── useRisk.js
│   ├── useApi.js
│   └── index.js
│
└── integration/        # Example integrations
    └── FraudDashboard.integration.jsx
```

## Services

### apiClient
Base HTTP client with authentication handling. Automatically adds Bearer token to requests.

```javascript
import { apiClient } from './services';

apiClient.setToken('your-jwt-token');
const data = await apiClient.get('/transactions');
```

### transactionService
Handle transaction-related API calls.

```javascript
import { transactionService } from './services';

// Fetch all transactions with filters
const result = await transactionService.fetchAll({ risk_level: 'HIGH', page: 1 });

// Search transactions
const results = await transactionService.search('CUST-1029');

// Import CSV
const importResult = await transactionService.importCSV(file);
```

### alertService
Handle alert management.

```javascript
import { alertService } from './services';

// Fetch alerts
const alerts = await alertService.fetchAll({ status: 'NEW' });

// Update alert status
await alertService.updateStatus(alertId, 'INVESTIGATING');

// Add investigation notes
await alertService.addNotes(alertId, 'Investigating unusual pattern');
```

### dashboardService
Fetch dashboard statistics.

```javascript
import { dashboardService } from './services';

// Get all dashboard data
const data = await dashboardService.getStats(14); // Last 14 days

// Get specific data
const trends = await dashboardService.getTrends(7);
const distribution = await dashboardService.getRiskDistribution();
```

### networkService
Fetch fraud network graph data.

```javascript
import { networkService } from './services';

// Get network graph
const graph = await networkService.getGraph({ customer_id: 'CUST-1029', depth: 2 });

// Get suspicious clusters
const clusters = await networkService.getClusters(3, 'HIGH');
```

### riskService
Score transactions for fraud risk.

```javascript
import { riskService } from './services';

// Score a transaction
const result = await riskService.scoreTransaction(transactionData);

// Get all risk flags
const flags = await riskService.getRiskFlags();
```

## Hooks

### useTransactions
```javascript
const {
  transactions,
  loading,
  error,
  pagination,
  fetchTransactions,
  searchTransactions,
  createTransaction,
  updateTransaction,
  importCSV,
} = useTransactions();
```

### useAlerts
```javascript
const {
  alerts,
  loading,
  error,
  stats,
  fetchAlerts,
  updateAlertStatus,
  addAlertNotes,
  assignAlert,
  fetchStats,
} = useAlerts();
```

### useDashboard
```javascript
const {
  dashboardData,
  trends,
  riskDistribution,
  suspiciousCustomers,
  suspiciousDevices,
  recentAlerts,
  loading,
  fetchDashboardData,
} = useDashboard();
```

### useNetwork
```javascript
const {
  graphData,
  clusters,
  loading,
  fetchGraph,
  fetchClusters,
  fetchGraphByCustomer,
} = useNetwork();
```

## Integration Example

```jsx
import React, { useEffect } from 'react';
import { useDashboard, useTransactions, useAlerts } from './hooks';

function Dashboard() {
  const { dashboardData, loading: dashLoading, fetchDashboardData } = useDashboard();
  const { transactions, loading: txLoading, fetchTransactions } = useTransactions();
  const { alerts, loading: alertsLoading, fetchAlerts } = useAlerts();

  useEffect(() => {
    fetchDashboardData(14);
    fetchTransactions({ page: 1, per_page: 20 });
    fetchAlerts({ per_page: 10 });
  }, []);

  if (dashLoading || txLoading || alertsLoading) return <div>Loading...</div>;

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Total Transactions: {dashboardData?.stats?.total_transactions}</p>
      <p>Open Alerts: {dashboardData?.stats?.open_alerts}</p>
      {/* Render charts and tables */}
    </div>
  );
}
```

## Error Handling

All hooks include error handling:
```javascript
const { error, fetchData } = useSomething();

useEffect(() => {
  fetchData().catch(err => {
    console.error('Failed to fetch:', err);
  });
}, []);

return error ? <div>Error: {error}</div> : <div>Data loaded</div>;
```

## API Endpoints

Backend API endpoints this layer calls:

| Service | Endpoint | Method |
|---------|----------|--------|
| Dashboard | `/api/v1/dashboard/stats` | GET |
| Dashboard | `/api/v1/dashboard/trends` | GET |
| Dashboard | `/api/v1/dashboard/risk-distribution` | GET |
| Transactions | `/api/v1/transactions` | GET |
| Transactions | `/api/v1/transactions/{id}` | GET |
| Transactions | `/api/v1/transactions/search` | GET |
| Transactions | `/api/v1/transactions/import/csv` | POST |
| Alerts | `/api/v1/alerts` | GET |
| Alerts | `/api/v1/alerts/{id}` | PATCH |
| Network | `/api/v1/risk/network/graph` | GET |
| Risk | `/api/v1/risk/score` | POST |
| Risk | `/api/v1/risk/flags` | GET |
