"use client";
import { useEffect, useState } from "react";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const navigation = ["Overview","Market Scanner","Opportunity Radar","Coin Intelligence","Historical Intelligence","Strategy Lab","Intraday Trading","Swing Trading","Paper Portfolio","Trading Journal","Performance Analytics","AI Mentor"];

export default function Home() {
  const [apiStatus, setApiStatus] = useState("Checking…");
  useEffect(() => {
    let active = true;
    fetch(`${apiBase}/health`).then(r => { if (!r.ok) throw new Error(); return r.json(); })
      .then(() => { if (active) setApiStatus("Connected"); })
      .catch(() => { if (active) setApiStatus("Unavailable"); });
    return () => { active = false; };
  }, []);
  return <div className="shell">
    <aside className="sidebar">
      <div className="brand">CRYPTO INTELLIGENCE<small>PERSONAL TRADING WORKSPACE</small></div>
      <div className="nav-label">Workspace</div>
      <nav className="nav-list" aria-label="Main navigation">{navigation.map((n,i)=><a key={n} className={`nav-item ${i===0?"active":""}`} href="#">{n}</a>)}</nav>
      <div className="nav-label">System</div><a className="nav-item" href="#">Settings</a>
    </aside>
    <main className="main">
      <header className="topbar"><div><div className="eyebrow">PERSONAL MARKET INTELLIGENCE</div><h1>Market Overview</h1><div className="muted">Research and paper-trading workspace</div></div><span className="status">P0 · PAPER ONLY</span></header>
      <section className="grid">
        <div className="card"><div className="metric-label">Simulation capital</div><div className="metric-value">₹5,000</div><div className="note">Proposed starting balance</div></div>
        <div className="card"><div className="metric-label">Assets monitored</div><div className="metric-value">—</div><div className="note">Market data not connected</div></div>
        <div className="card"><div className="metric-label">Open paper positions</div><div className="metric-value">0</div><div className="note">No simulated orders yet</div></div>
        <div className="card"><div className="metric-label">API connection</div><div className="metric-value" style={{fontSize:18}}>{apiStatus}</div><div className="note">Backend health check</div></div>
      </section>
      <section className="section"><div className="section-head"><h2>Trading engines</h2><span className="pill">P0 foundation</span></div><div className="grid" style={{gridTemplateColumns:"repeat(auto-fit,minmax(220px,1fr))"}}>
        <div className="card"><h2>Intraday engine</h2><p className="note">30–50 liquid cryptocurrencies; 5-minute entry analysis and 15-minute trend confirmation.</p><span className="pill">Not connected</span></div>
        <div className="card"><h2>Swing intelligence</h2><p className="note">Broader digital-asset research. Stablecoins are treated as liquidity reserves; tokenised assets require eligibility checks.</p><span className="pill">Not connected</span></div>
      </div></section>
      <section className="section card"><div className="section-head"><h2>Opportunity radar</h2><span className="pill">Awaiting verified data</span></div><p className="note">No prices or buy/sell signals are shown until a market-data provider is configured and validated.</p></section>
      <section className="section card"><div className="section-head"><h2>Investment universe</h2><span className="pill">Final selection in M2</span></div><div className="table-wrap"><table><thead><tr><th>Category</th><th>Purpose</th><th>Status</th></tr></thead><tbody>
        <tr><td>Major cryptocurrencies</td><td>Intraday and swing</td><td>Pending selection</td></tr><tr><td>Established altcoins</td><td>Intraday and swing</td><td>Liquidity screening</td></tr><tr><td>Emerging digital assets</td><td>Selective swing research</td><td>Eligibility screening</td></tr><tr><td>Stablecoins</td><td>Liquidity and reserves</td><td>Reserve category</td></tr><tr><td>Tokenised assets</td><td>Conditional swing research</td><td>Issuer/redemption checks</td></tr>
      </tbody></table></div></section>
      <div className="footer">P0 foundation preview · No live trading · No investment recommendations · Market data not yet connected</div>
    </main>
  </div>;
}
