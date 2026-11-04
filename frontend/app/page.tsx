"use client";
import { FormEvent, useEffect, useState } from "react";

const navigation = ["Overview","Market Scanner","Opportunity Radar","Coin Intelligence","Historical Intelligence","Strategy Lab","Intraday Trading","Swing Trading","Paper Portfolio","Trading Journal","Performance Analytics","AI Mentor"];
type Diagnostics = { data_available?: boolean; coverage_groups?: number; fresh_groups?: number; stale_groups?: number; coverage?: Array<{venue:string;symbol:string;interval:string;closed_candle_count:number;age_seconds:number;fresh:boolean}> };
type Portfolio = { cash?: number; open_positions?: number; realised_pnl?: number };

export default function Home() {
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState("");
  const [apiStatus, setApiStatus] = useState("Checking…");
  const [diagnostics, setDiagnostics] = useState<Diagnostics | null>(null);
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [system, setSystem] = useState<Record<string, unknown> | null>(null);

  async function refreshDashboard() {
    try {
      const [health, diag, status, account] = await Promise.all([
        fetch("/api/backend/health", { cache: "no-store" }),
        fetch("/api/backend/market-data/diagnostics", { cache: "no-store" }),
        fetch("/api/backend/system/status", { cache: "no-store" }),
        fetch("/api/backend/paper/portfolio", { cache: "no-store" }),
      ]);
      setApiStatus(health.ok ? "Connected" : "Not connected");
      if (diag.ok) setDiagnostics(await diag.json());
      if (status.ok) setSystem(await status.json());
      if (account.ok) setPortfolio(await account.json());
    } catch {
      setApiStatus("Unavailable");
    }
  }

  useEffect(() => {
    let active = true;
    fetch("/api/session", { cache: "no-store" }).then(response => {
      if (active) setAuthenticated(response.ok);
    }).catch(() => {
      if (active) setAuthenticated(false);
    });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!authenticated) return;
    void refreshDashboard();
    const timer = window.setInterval(() => void refreshDashboard(), 30000);
    return () => window.clearInterval(timer);
  }, [authenticated]);

  async function login(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoginError("");
    const response = await fetch("/api/session", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      setLoginError(body.detail ?? "Unable to sign in.");
      return;
    }
    setPassword("");
    setAuthenticated(true);
  }

  async function logout() {
    await fetch("/api/session", { method: "DELETE" });
    setAuthenticated(false);
    setDiagnostics(null);
    setPortfolio(null);
  }

  if (authenticated === null) {
    return <main className="main"><div className="card">Checking secure dashboard session…</div></main>;
  }
  if (!authenticated) {
    return <main className="main" style={{maxWidth:480,margin:"10vh auto"}}>
      <form className="card" onSubmit={login}>
        <div className="eyebrow">PRIVATE WORKSPACE</div><h1>Crypto Intelligence</h1>
        <p className="note">Sign in to access your personal market and paper-trading dashboard.</p>
        <label htmlFor="dashboard-password" className="metric-label">Dashboard password</label>
        <input id="dashboard-password" type="password" autoComplete="current-password" value={password}
          onChange={event=>setPassword(event.target.value)} required
          style={{display:"block",width:"100%",padding:12,margin:"10px 0 16px",background:"#0b1220",color:"white",border:"1px solid #26364e",borderRadius:8}} />
        <button type="submit" style={{padding:"11px 16px",border:0,borderRadius:8,cursor:"pointer"}}>Sign in</button>
        {loginError && <p role="alert" className="note">{loginError}</p>}
      </form>
    </main>;
  }

  const coverage = diagnostics?.coverage ?? [];
  const modules = (system?.modules as Record<string,string>) ?? {};
  return <div className="shell">
    <aside className="sidebar">
      <div className="brand">CRYPTO INTELLIGENCE<small>PERSONAL TRADING WORKSPACE</small></div>
      <div className="nav-label">Workspace</div>
      <nav className="nav-list" aria-label="Main navigation">{navigation.map((n,i)=><a key={n} className={`nav-item ${i===0?"active":""}`} href={`#section-${i}`}>{n}</a>)}</nav>
      <div className="nav-label">System</div><a className="nav-item" href="#system">System status</a>
    </aside>
    <main className="main">
      <header className="topbar"><div><div className="eyebrow">PERSONAL MARKET INTELLIGENCE</div><h1>Market Overview</h1><div className="muted">Research and paper-trading workspace</div></div><div><span className="status">PAPER ONLY · NO LIVE ORDERS</span><button onClick={()=>void logout()} style={{marginLeft:10,padding:8}}>Sign out</button></div></header>
      <section className="grid" id="section-0">
        <div className="card"><div className="metric-label">Paper cash</div><div className="metric-value">{portfolio ? `₹${portfolio.cash?.toLocaleString("en-IN",{maximumFractionDigits:2})}` : "—"}</div><div className="note">Virtual INR balance</div></div>
        <div className="card"><div className="metric-label">Data coverage groups</div><div className="metric-value">{diagnostics?.coverage_groups ?? "—"}</div><div className="note">{diagnostics?.fresh_groups ?? 0} fresh · {diagnostics?.stale_groups ?? 0} stale</div></div>
        <div className="card"><div className="metric-label">Open paper positions</div><div className="metric-value">{portfolio?.open_positions ?? "—"}</div><div className="note">Persistent paper ledger</div></div>
        <div className="card"><div className="metric-label">API connection</div><div className="metric-value" style={{fontSize:18}}>{apiStatus}</div><div className="note">Server-side health check</div></div>
      </section>
      <section className="section" id="section-6"><div className="section-head"><h2>Trading engines</h2><span className="pill">Independent strategies</span></div><div className="grid" style={{gridTemplateColumns:"repeat(auto-fit,minmax(220px,1fr))"}}>
        <div className="card"><h2>Intraday engine</h2><p className="note">5-minute entry analysis with 15-minute trend confirmation. Long-only paper simulation; no forced trade frequency.</p><span className="pill">Scanner API ready</span></div>
        <div className="card" id="section-7"><h2>Swing intelligence</h2><p className="note">4-hour entry analysis with daily trend confirmation. Stablecoins remain liquidity reserves; tokenised assets require eligibility checks.</p><span className="pill">Scanner API ready</span></div>
      </div></section>
      <section className="section card" id="section-1"><div className="section-head"><h2>Opportunity radar</h2><span className="pill">Fresh data required</span></div><p className="note">Both entry and confirmation timeframes must align. No Trade is valid. Stale or incomplete candles never create a signal.</p></section>
      <section className="section card" id="section-2"><div className="section-head"><h2>Market data coverage</h2><span className="pill">{diagnostics?.data_available ? "Stored candles found" : "Awaiting feed"}</span></div><div className="table-wrap"><table><thead><tr><th>Venue</th><th>Pair</th><th>Interval</th><th>Closed candles</th><th>Age (sec)</th><th>Quality</th></tr></thead><tbody>{coverage.length ? coverage.map((row,i)=><tr key={`${row.venue}-${row.symbol}-${row.interval}-${i}`}><td>{row.venue}</td><td>{row.symbol}</td><td>{row.interval}</td><td>{row.closed_candle_count}</td><td>{row.age_seconds}</td><td>{row.fresh?"Fresh":"Stale"}</td></tr>) : <tr><td colSpan={6}>No stored market candles. Live feed has not been verified.</td></tr>}</tbody></table></div></section>
      <section className="section grid" style={{gridTemplateColumns:"repeat(auto-fit,minmax(220px,1fr))"}}>
        <div className="card" id="section-8"><h2>Paper portfolio</h2><p className="note">Cash ₹{portfolio?.cash?.toLocaleString("en-IN",{maximumFractionDigits:2}) ?? "—"} · {portfolio?.open_positions ?? 0} open positions · realised P&L ₹{portfolio?.realised_pnl?.toFixed(2) ?? "—"}.</p><span className="pill">Long-only ledger</span></div>
        <div className="card" id="section-9"><h2>Risk Guardian</h2><p className="note">1% risk per trade, 2% daily loss, 5% weekly loss, maximum four open positions and 20% per-asset exposure defaults.</p><span className="pill">Deterministic controls</span></div>
        <div className="card" id="section-10"><h2>Backtesting</h2><p className="note">Long-only SMA crossover simulation includes configurable fees and slippage. Out-of-sample validation remains essential.</p><span className="pill">API ready</span></div>
        <div className="card" id="section-11"><h2>AI Mentor</h2><p className="note">Deterministic evidence summaries are available. Optional language-model explanations cannot override risk decisions or submit orders.</p><span className="pill">Explain only</span></div>
      </section>
      <section className="section card" id="system"><div className="section-head"><h2>System capabilities</h2><span className="pill">M3–M10 foundation</span></div><div className="note">{Object.entries(modules).map(([key,value])=><p key={key}><strong>{key.replaceAll("_"," ")}:</strong> {value}</p>)}</div></section>
      <div className="footer">No live trading · No leverage · No guaranteed returns · No financial advice · Backend deployment and live market-feed validation remain external operational gates.</div>
    </main>
  </div>;
}
