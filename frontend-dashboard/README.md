# Sentinel Fraud & Risk Dashboard

Sentinel is a React dashboard UI for monitoring fraud and transaction risk. It gives analysts a single view of transaction volume, risk distribution, live alerts, suspicious customers, and suspicious devices or IP addresses.

This repository currently contains the frontend dashboard and uses mock data for demonstration. Backend APIs, authentication, database persistence, and production AI/ML scoring are planned integration points for the next phase.

## Dashboard Features

- KPI cards for total transactions, high-risk transactions, medium-risk transactions, confirmed fraud, false positives, open alerts, and average risk score
- Transaction and high-risk trend chart
- Risk distribution chart
- Live fraud alerts with severity, score, reason, and status
- Suspicious customer risk profiles
- Suspicious device and IP address list
- Search transactions by ID or customer
- Filter transactions by Low, Medium, and High risk
- Responsive dark risk-intelligence interface

## Tech Stack

- React 19
- Vite
- Tailwind CSS 4
- Recharts
- Lucide React
- Oxlint

## Getting Started

Requirements: Node.js 20 or newer.

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Create a production build:

```bash
npm run build
```

Run linting:

```bash
npm run lint
```

## Project Structure

```text
src/
	App.jsx              Application entry component
	FraudDashboard.jsx   Dashboard UI and mock fraud data
	index.css            Global styles and Tailwind import
	main.jsx             React bootstrap
	assets/              Static frontend assets
```

## Data and Scope

Dashboard values are currently defined as local mock data in `src/FraudDashboard.jsx`. The next implementation phase can connect these views to a FastAPI/PostgreSQL backend for real transactions, authentication, rule-based scoring, ML anomaly detection, investigations, reports, and external transaction APIs.
# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some Oxlint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the Oxlint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and Oxlint's TypeScript related rules in your project.
