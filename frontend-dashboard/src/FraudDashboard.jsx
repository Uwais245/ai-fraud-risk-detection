import React, { useState, useMemo } from "react";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar
} from "recharts";
import {
  ShieldAlert, LayoutGrid, Receipt, Bell, Search as SearchIcon, Users,
  Network, SlidersHorizontal, FileText, Settings, ChevronDown, TrendingUp,
  TrendingDown, Smartphone, MapPin, Wifi, MoreHorizontal, ArrowUpRight
} from "lucide-react";

// ---------------------------------------------------------------------------
// Design tokens — a risk-driven palette: the three signal colors (calm green /
// amber / coral) ARE the accent system, because risk level is the one thing
// every screen in this product needs to communicate at a glance.
// ---------------------------------------------------------------------------
const c = {
  bg: "#0D121D",
  panel: "#131a29",
  surface: "#161f31",
  surfaceHover: "#1b2438",
  border: "#232d43",
  borderLight: "#303c58",
  text: "#E7EAF3",
  textDim: "#8992AA",
  textFaint: "#5B6480",
  brand: "#5B7FFF",
  brandDim: "rgba(91,127,255,0.13)",
  low: "#33D69F",
  lowDim: "rgba(51,214,159,0.13)",
  med: "#F5A623",
  medDim: "rgba(245,166,35,0.14)",
  high: "#FF5C72",
  highDim: "rgba(255,92,114,0.14)",
};

const FONT_UI = "'Inter', ui-sans-serif, system-ui, sans-serif";
const FONT_MONO = "'IBM Plex Mono', ui-monospace, SFMono-Regular, monospace";

// ---------------------------------------------------------------------------
// Mock data — stands in for the real /api/dashboard, /api/transactions,
// /api/alerts endpoints the backend module will expose.
// ---------------------------------------------------------------------------
const trend = [
  { d: "Aug 27", tx: 2840, high: 18 }, { d: "Aug 28", tx: 3010, high: 22 },
  { d: "Aug 29", tx: 2760, high: 15 }, { d: "Aug 30", tx: 3320, high: 27 },
  { d: "Aug 31", tx: 3580, high: 31 }, { d: "Sep 01", tx: 3195, high: 24 },
  { d: "Sep 02", tx: 3410, high: 29 }, { d: "Sep 03", tx: 3705, high: 34 },
  { d: "Sep 04", tx: 3920, high: 38 }, { d: "Sep 05", tx: 3640, high: 30 },
  { d: "Sep 06", tx: 3380, high: 26 }, { d: "Sep 07", tx: 3990, high: 41 },
  { d: "Sep 08", tx: 4210, high: 47 }, { d: "Sep 09", tx: 3860, high: 35 },
];

const riskSplit = [
  { name: "Low", value: 68, color: c.low },
  { name: "Medium", value: 24, color: c.med },
  { name: "High", value: 8, color: c.high },
];

const alerts = [
  { id: "AL-4821", customer: "CUST-1029", score: 91, sev: "high", reason: "New device + 3 transactions in 5 minutes", time: "2m ago", status: "New" },
  { id: "AL-4820", customer: "CUST-2287", score: 76, sev: "high", reason: "Location differs from all prior activity", time: "11m ago", status: "Investigating" },
  { id: "AL-4818", customer: "CUST-0552", score: 58, sev: "med", reason: "Spend 6x above customer average", time: "34m ago", status: "New" },
  { id: "AL-4815", customer: "CUST-3110", score: 63, sev: "med", reason: "Same device linked to 4 accounts", time: "1h ago", status: "Investigating" },
  { id: "AL-4809", customer: "CUST-1774", score: 88, sev: "high", reason: "IP shared by 9 distinct customers", time: "2h ago", status: "New" },
];

const suspiciousCustomers = [
  { id: "CUST-1029", level: "High", score: 91, tx: 128, flagged: 7, devices: 4, locations: 3 },
  { id: "CUST-1774", level: "High", score: 88, tx: 64, flagged: 5, devices: 3, locations: 4 },
  { id: "CUST-2287", level: "Medium", score: 76, tx: 205, flagged: 3, devices: 2, locations: 2 },
  { id: "CUST-3110", level: "Medium", score: 63, tx: 41, flagged: 2, devices: 4, locations: 1 },
];

const suspiciousEntities = [
  { type: "Device", value: "iPhone 15 · DEV-8F31", detail: "14 accounts · 32 flagged txns", icon: Smartphone, tone: { col: c.high, bg: c.highDim } },
  { type: "IP address", value: "185.72.14.91", detail: "9 customers · 5 countries", icon: Wifi, tone: { col: c.med, bg: c.medDim } },
  { type: "Device", value: "MacBook Air · DEV-4C09", detail: "7 accounts · 18 flagged txns", icon: Smartphone, tone: { col: c.high, bg: c.highDim } },
  { type: "IP address", value: "103.12.88.204", detail: "6 customers · 3 countries", icon: Wifi, tone: { col: c.med, bg: c.medDim } },
];

const transactions = [
  { id: "TXN-99213", customer: "CUST-1029", amount: 1200, method: "Card", location: "Lahore, PK", device: "iPhone 15 (new)", score: 87, status: "Review", time: "09:41" },
  { id: "TXN-99212", customer: "CUST-4487", amount: 84, method: "Wallet", location: "Karachi, PK", device: "Pixel 8", score: 12, status: "Approved", time: "09:38" },
  { id: "TXN-99211", customer: "CUST-2287", amount: 640, method: "Card", location: "Dubai, AE", device: "MacBook Air", score: 76, status: "Review", time: "09:31" },
  { id: "TXN-99210", customer: "CUST-0552", amount: 300, method: "Bank", location: "Islamabad, PK", device: "Galaxy S23", score: 58, status: "Approved", time: "09:22" },
  { id: "TXN-99209", customer: "CUST-1774", amount: 2100, method: "Card", location: "Doha, QA", device: "iPhone 13", score: 88, status: "Blocked", time: "09:15" },
  { id: "TXN-99208", customer: "CUST-8821", amount: 46, method: "Wallet", location: "Lahore, PK", device: "iPhone 14", score: 6, status: "Approved", time: "09:09" },
];

const nav = [
  { label: "Dashboard", icon: LayoutGrid },
  { label: "Transactions", icon: Receipt },
  { label: "Alerts", icon: Bell, badge: 47 },
  { label: "Customers", icon: Users },
  { label: "Fraud Network", icon: Network },
  { label: "Rules Engine", icon: SlidersHorizontal },
  { label: "Reports", icon: FileText },
];

function riskTone(score) {
  if (score >= 71) return { col: c.high, bg: c.highDim, label: "High" };
  if (score >= 31) return { col: c.med, bg: c.medDim, label: "Medium" };
  return { col: c.low, bg: c.lowDim, label: "Low" };
}

function Badge({ children, tone }) {
  return (
    <span
      className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
      style={{ background: tone.bg, color: tone.col, fontFamily: FONT_UI }}
    >
      {children}
    </span>
  );
}

function KpiCard({ icon: Icon, label, value, delta, up, tone }) {
  return (
    <div
      className="rounded-lg p-5 flex flex-col gap-3"
      style={{ background: c.surface, border: `1px solid ${c.border}` }}
    >
      <div className="flex items-center justify-between">
        <div
          className="w-9 h-9 rounded-md flex items-center justify-center"
          style={{ background: tone ? tone.bg : c.brandDim, color: tone ? tone.col : c.brand }}
        >
          <Icon size={17} strokeWidth={2} />
        </div>
        <div
          className="flex items-center gap-1 text-xs"
          style={{ color: up ? c.low : c.textDim, fontFamily: FONT_MONO }}
        >
          {up ? <TrendingUp size={13} /> : <TrendingDown size={13} />}
          {delta}
        </div>
      </div>
      <div>
        <div style={{ fontFamily: FONT_MONO, fontSize: 26, fontWeight: 600, color: c.text, letterSpacing: "-0.02em" }}>
          {value}
        </div>
        <div style={{ color: c.textDim, fontSize: 13, marginTop: 2 }}>{label}</div>
      </div>
    </div>
  );
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) return null;
  return (
    <div
      className="rounded-md px-3 py-2 text-xs"
      style={{ background: c.panel, border: `1px solid ${c.borderLight}`, fontFamily: FONT_MONO, color: c.text }}
    >
      <div style={{ color: c.textDim, marginBottom: 4 }}>{label}</div>
      {payload.map((p) => (
        <div key={p.dataKey} style={{ color: p.color }}>
          {p.dataKey === "tx" ? "Transactions" : "High-risk"}: {p.value.toLocaleString()}
        </div>
      ))}
    </div>
  );
}

export default function FraudDashboard() {
  const [active, setActive] = useState("Dashboard");
  const [query, setQuery] = useState("");
  const [levelFilter, setLevelFilter] = useState("All");

  const filteredTx = useMemo(() => {
    return transactions.filter((t) => {
      const matchesQuery =
        !query ||
        t.id.toLowerCase().includes(query.toLowerCase()) ||
        t.customer.toLowerCase().includes(query.toLowerCase());
      const tone = riskTone(t.score).label;
      const matchesLevel = levelFilter === "All" || tone === levelFilter;
      return matchesQuery && matchesLevel;
    });
  }, [query, levelFilter]);

  return (
    <div style={{ fontFamily: FONT_UI, background: c.bg, color: c.text, minHeight: "100vh" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-thumb { background: ${c.borderLight}; border-radius: 8px; }
        table { border-collapse: collapse; width: 100%; }
      `}</style>

      <div className="flex">
        {/* Sidebar */}
        <aside
          className="hidden md:flex flex-col shrink-0"
          style={{ width: 224, background: c.panel, borderRight: `1px solid ${c.border}`, minHeight: "100vh" }}
        >
          <div className="flex items-center gap-2 px-5 py-5">
            <div
              className="w-8 h-8 rounded-md flex items-center justify-center"
              style={{ background: c.brand }}
            >
              <ShieldAlert size={17} color="#fff" strokeWidth={2.2} />
            </div>
            <div>
              <div style={{ fontWeight: 600, fontSize: 14.5, letterSpacing: "-0.01em" }}>Sentinel</div>
              <div style={{ fontSize: 10.5, color: c.textFaint }}>Risk Intelligence</div>
            </div>
          </div>

          <nav className="flex-1 px-3 mt-2 flex flex-col gap-0.5">
            {nav.map((item) => {
              const isActive = active === item.label;
              return (
                <button
                  key={item.label}
                  onClick={() => setActive(item.label)}
                  className="flex items-center gap-2.5 px-3 py-2 rounded-md text-sm text-left transition-colors"
                  style={{
                    background: isActive ? c.brandDim : "transparent",
                    color: isActive ? c.brand : c.textDim,
                    fontWeight: isActive ? 600 : 500,
                  }}
                >
                  <item.icon size={16} strokeWidth={2} />
                  <span className="flex-1">{item.label}</span>
                  {item.badge && (
                    <span
                      style={{ background: c.highDim, color: c.high, fontFamily: FONT_MONO }}
                      className="text-[10px] px-1.5 py-0.5 rounded-full"
                    >
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>

          <div className="px-3 pb-4">
            <button
              className="flex items-center gap-2.5 px-3 py-2 rounded-md text-sm w-full"
              style={{ color: c.textDim }}
            >
              <Settings size={16} strokeWidth={2} />
              Settings
            </button>
            <div
              className="mt-2 flex items-center gap-2.5 px-3 py-2.5 rounded-md"
              style={{ background: c.surface, border: `1px solid ${c.border}` }}
            >
              <div
                className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold"
                style={{ background: c.brand, color: "#fff" }}
              >
                UA
              </div>
              <div className="leading-tight">
                <div style={{ fontSize: 12.5, fontWeight: 600 }}>Uwais Abro</div>
                <div style={{ fontSize: 10.5, color: c.textFaint }}>Analyst</div>
              </div>
            </div>
          </div>
        </aside>

        {/* Main */}
        <main className="flex-1 min-w-0">
          {/* Topbar */}
          <div
            className="flex items-center gap-4 px-6 py-4 sticky top-0 z-10"
            style={{ background: "rgba(13,18,29,0.92)", backdropFilter: "blur(8px)", borderBottom: `1px solid ${c.border}` }}
          >
            <div>
              <h1 style={{ fontSize: 18, fontWeight: 600, letterSpacing: "-0.01em" }}>Fraud &amp; Risk Overview</h1>
              <p style={{ fontSize: 12.5, color: c.textFaint, marginTop: 1 }}>Last 14 days · updated live</p>
            </div>
            <div className="flex-1" />
            <div
              className="hidden sm:flex items-center gap-2 px-3 py-2 rounded-md"
              style={{ background: c.surface, border: `1px solid ${c.border}`, width: 260 }}
            >
              <SearchIcon size={15} color={c.textFaint} />
              <input
                placeholder="Search customer, transaction ID…"
                className="bg-transparent outline-none w-full text-sm"
                style={{ color: c.text }}
              />
            </div>
            <button
              className="flex items-center gap-1.5 px-3 py-2 rounded-md text-sm"
              style={{ background: c.surface, border: `1px solid ${c.border}`, color: c.textDim }}
            >
              Last 14 days <ChevronDown size={14} />
            </button>
            <div className="relative">
              <Bell size={18} color={c.textDim} />
              <span
                className="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full flex items-center justify-center"
                style={{ background: c.high, fontSize: 8, fontFamily: FONT_MONO, color: "#fff" }}
              >
                9
              </span>
            </div>
          </div>

          <div className="p-6 flex flex-col gap-5">
            {/* KPIs */}
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
              <KpiCard icon={Receipt} label="Total transactions" value="48,206" delta="+12.4%" up tone={{ col: c.brand, bg: c.brandDim }} />
              <KpiCard icon={ShieldAlert} label="High-risk transactions" value="312" delta="+3.1%" up tone={{ col: c.high, bg: c.highDim }} />
              <KpiCard icon={SlidersHorizontal} label="Medium-risk transactions" value="1,124" delta="+5.6%" up tone={{ col: c.med, bg: c.medDim }} />
              <KpiCard icon={ShieldAlert} label="Confirmed fraud" value="86" delta="+2.4%" up tone={{ col: c.high, bg: c.highDim }} />
              <KpiCard icon={Bell} label="False positives" value="29" delta="-11.8%" tone={{ col: c.low, bg: c.lowDim }} />
              <KpiCard icon={Bell} label="Open fraud alerts" value="47" delta="-8.2%" tone={{ col: c.med, bg: c.medDim }} />
              <KpiCard icon={TrendingUp} label="Average risk score" value="34.6" delta="+1.8 pts" up tone={{ col: c.low, bg: c.lowDim }} />
            </div>

            {/* Charts row */}
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
              <div
                className="xl:col-span-2 rounded-lg p-5"
                style={{ background: c.surface, border: `1px solid ${c.border}` }}
              >
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 600 }}>Transaction &amp; risk trend</div>
                    <div style={{ fontSize: 12, color: c.textFaint }}>Daily volume vs. high-risk count</div>
                  </div>
                  <div className="flex items-center gap-3 text-xs" style={{ color: c.textDim }}>
                    <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full" style={{ background: c.brand }} />Transactions</span>
                    <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full" style={{ background: c.high }} />High-risk</span>
                  </div>
                </div>
                <ResponsiveContainer width="100%" height={220}>
                  <AreaChart data={trend} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="txGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor={c.brand} stopOpacity={0.35} />
                        <stop offset="100%" stopColor={c.brand} stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid stroke={c.border} vertical={false} />
                    <XAxis dataKey="d" tick={{ fill: c.textFaint, fontSize: 11 }} axisLine={{ stroke: c.border }} tickLine={false} />
                    <YAxis tick={{ fill: c.textFaint, fontSize: 11 }} axisLine={false} tickLine={false} />
                    <Tooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey="tx" stroke={c.brand} strokeWidth={2} fill="url(#txGrad)" />
                    <Area type="monotone" dataKey="high" stroke={c.high} strokeWidth={2} fill="transparent" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              <div
                className="rounded-lg p-5 flex flex-col"
                style={{ background: c.surface, border: `1px solid ${c.border}` }}
              >
                <div style={{ fontSize: 14, fontWeight: 600 }}>Risk distribution</div>
                <div style={{ fontSize: 12, color: c.textFaint, marginBottom: 8 }}>Share of today's transactions</div>
                <ResponsiveContainer width="100%" height={160}>
                  <PieChart>
                    <Pie data={riskSplit} dataKey="value" innerRadius={48} outerRadius={68} paddingAngle={3} stroke="none">
                      {riskSplit.map((r) => (
                        <Cell key={r.name} fill={r.color} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
                <div className="flex flex-col gap-2 mt-1">
                  {riskSplit.map((r) => (
                    <div key={r.name} className="flex items-center justify-between text-xs">
                      <span className="flex items-center gap-2" style={{ color: c.textDim }}>
                        <span className="w-2 h-2 rounded-full" style={{ background: r.color }} />
                        {r.name}
                      </span>
                      <span style={{ fontFamily: FONT_MONO, color: c.text }}>{r.value}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Alerts + Suspicious customers + devices/IPs */}
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
              <div
                className="xl:col-span-2 rounded-lg"
                style={{ background: c.surface, border: `1px solid ${c.border}` }}
              >
                <div className="flex items-center justify-between px-5 py-4" style={{ borderBottom: `1px solid ${c.border}` }}>
                  <div style={{ fontSize: 14, fontWeight: 600 }}>Live fraud alerts</div>
                  <button style={{ fontSize: 12.5, color: c.brand }} className="flex items-center gap-1">
                    View all <ArrowUpRight size={13} />
                  </button>
                </div>
                <div>
                  {alerts.map((a) => {
                    const tone = a.sev === "high" ? { col: c.high, bg: c.highDim } : { col: c.med, bg: c.medDim };
                    return (
                      <div
                        key={a.id}
                        className="flex items-center gap-4 px-5 py-3.5"
                        style={{ borderLeft: `3px solid ${tone.col}`, borderBottom: `1px solid ${c.border}` }}
                      >
                        <div
                          style={{ fontFamily: FONT_MONO, fontSize: 15, fontWeight: 600, color: tone.col, width: 34 }}
                        >
                          {a.score}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span style={{ fontSize: 13, fontWeight: 600 }}>{a.customer}</span>
                            <span style={{ fontSize: 11, color: c.textFaint, fontFamily: FONT_MONO }}>{a.id}</span>
                          </div>
                          <div style={{ fontSize: 12.5, color: c.textDim, marginTop: 1 }}>{a.reason}</div>
                        </div>
                        <div className="text-right shrink-0">
                          <div style={{ fontSize: 11, color: c.textFaint }}>{a.time}</div>
                          <Badge tone={a.status === "New" ? { col: c.brand, bg: c.brandDim } : { col: c.textDim, bg: c.border }}>
                            {a.status}
                          </Badge>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="rounded-lg" style={{ background: c.surface, border: `1px solid ${c.border}` }}>
                <div className="px-5 py-4" style={{ borderBottom: `1px solid ${c.border}` }}>
                  <div style={{ fontSize: 14, fontWeight: 600 }}>Suspicious customers</div>
                  <div style={{ fontSize: 12, color: c.textFaint }}>Ranked by risk score</div>
                </div>
                <div className="flex flex-col">
                  {suspiciousCustomers.map((cust) => {
                    const tone = riskTone(cust.score);
                    return (
                      <div key={cust.id} className="flex items-center gap-3 px-5 py-3" style={{ borderBottom: `1px solid ${c.border}` }}>
                        <div className="flex-1 min-w-0">
                          <div style={{ fontSize: 13, fontWeight: 600 }}>{cust.id}</div>
                          <div className="flex items-center gap-2.5 mt-1" style={{ fontSize: 11, color: c.textFaint }}>
                            <span className="flex items-center gap-1"><Smartphone size={11} />{cust.devices}</span>
                            <span className="flex items-center gap-1"><MapPin size={11} />{cust.locations}</span>
                            <span className="flex items-center gap-1"><Wifi size={11} />{cust.flagged} flagged</span>
                          </div>
                        </div>
                        <Badge tone={tone}>{cust.score}</Badge>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="rounded-lg" style={{ background: c.surface, border: `1px solid ${c.border}` }}>
                <div className="px-5 py-4" style={{ borderBottom: `1px solid ${c.border}` }}>
                  <div style={{ fontSize: 14, fontWeight: 600 }}>Suspicious devices &amp; IPs</div>
                  <div style={{ fontSize: 12, color: c.textFaint }}>Most connected risk signals</div>
                </div>
                <div className="flex flex-col">
                  {suspiciousEntities.map((entity) => {
                    const Icon = entity.icon;
                    return (
                      <div key={entity.value} className="flex items-center gap-3 px-5 py-3" style={{ borderBottom: `1px solid ${c.border}` }}>
                        <div
                          className="w-8 h-8 rounded-md flex items-center justify-center shrink-0"
                          style={{ background: entity.tone.bg, color: entity.tone.col }}
                        >
                          <Icon size={15} />
                        </div>
                        <div className="min-w-0">
                          <div style={{ fontSize: 11, color: c.textFaint }}>{entity.type}</div>
                          <div style={{ fontSize: 12.5, fontWeight: 600, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{entity.value}</div>
                          <div style={{ fontSize: 11, color: c.textDim, marginTop: 2 }}>{entity.detail}</div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Transactions table */}
            <div className="rounded-lg" style={{ background: c.surface, border: `1px solid ${c.border}` }}>
              <div className="flex flex-wrap items-center gap-3 px-5 py-4" style={{ borderBottom: `1px solid ${c.border}` }}>
                <div style={{ fontSize: 14, fontWeight: 600 }} className="mr-auto">Recent transactions</div>
                <div
                  className="flex items-center gap-2 px-3 py-1.5 rounded-md"
                  style={{ background: c.panel, border: `1px solid ${c.border}` }}
                >
                  <SearchIcon size={13} color={c.textFaint} />
                  <input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Filter by ID or customer"
                    className="bg-transparent outline-none text-xs"
                    style={{ color: c.text, width: 160 }}
                  />
                </div>
                <div className="flex items-center gap-1 rounded-md p-1" style={{ background: c.panel, border: `1px solid ${c.border}` }}>
                  {["All", "Low", "Medium", "High"].map((lvl) => (
                    <button
                      key={lvl}
                      onClick={() => setLevelFilter(lvl)}
                      className="px-2.5 py-1 rounded text-xs"
                      style={{
                        background: levelFilter === lvl ? c.brandDim : "transparent",
                        color: levelFilter === lvl ? c.brand : c.textDim,
                        fontWeight: levelFilter === lvl ? 600 : 500,
                      }}
                    >
                      {lvl}
                    </button>
                  ))}
                </div>
              </div>

              <div className="overflow-x-auto">
                <table>
                  <thead>
                    <tr style={{ color: c.textFaint, fontSize: 11.5, textAlign: "left" }}>
                      {["Transaction", "Customer", "Amount", "Method", "Location", "Device", "Risk", "Status", ""].map((h) => (
                        <th key={h} className="px-5 py-2 font-medium" style={{ borderBottom: `1px solid ${c.border}` }}>
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {filteredTx.map((t) => {
                      const tone = riskTone(t.score);
                      const statusTone =
                        t.status === "Approved" ? { col: c.low, bg: c.lowDim }
                        : t.status === "Blocked" ? { col: c.high, bg: c.highDim }
                        : { col: c.med, bg: c.medDim };
                      return (
                        <tr key={t.id} style={{ fontSize: 12.5, borderBottom: `1px solid ${c.border}` }}>
                          <td className="px-5 py-3" style={{ fontFamily: FONT_MONO, color: c.text }}>{t.id}</td>
                          <td className="px-5 py-3" style={{ color: c.textDim }}>{t.customer}</td>
                          <td className="px-5 py-3" style={{ fontFamily: FONT_MONO, color: c.text }}>${t.amount.toLocaleString()}</td>
                          <td className="px-5 py-3" style={{ color: c.textDim }}>{t.method}</td>
                          <td className="px-5 py-3" style={{ color: c.textDim }}>{t.location}</td>
                          <td className="px-5 py-3" style={{ color: c.textDim }}>{t.device}</td>
                          <td className="px-5 py-3"><Badge tone={tone}>{t.score} · {tone.label}</Badge></td>
                          <td className="px-5 py-3"><Badge tone={statusTone}>{t.status}</Badge></td>
                          <td className="px-5 py-3"><MoreHorizontal size={15} color={c.textFaint} /></td>
                        </tr>
                      );
                    })}
                    {filteredTx.length === 0 && (
                      <tr>
                        <td colSpan={9} className="px-5 py-8 text-center" style={{ color: c.textFaint, fontSize: 13 }}>
                          No transactions match this filter.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
