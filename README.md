# Crypto Intelligence & Trading Assistant

Personal, learning-first digital-asset intelligence and paper-trading system.

## P0
- Desktop website, responsive mobile website and installable PWA.
- Intraday universe: 30–50 liquid cryptocurrencies.
- Swing universe: broader digital assets; stablecoins are liquidity/reserve instruments.
- Historical intelligence, quantitative analysis, backtesting, paper trading, risk controls, portfolio accounting and AI explanations.
- No live exchange order execution in P0.

## Local setup
Prerequisites: Docker Desktop with Compose, Node.js 20+, Python 3.11+.

1. Copy `.env.example` to `.env`.
2. Run `docker compose up --build`.
3. Website: http://localhost:3000
4. API health: http://localhost:8000/health
5. API docs: http://localhost:8000/docs

Never commit `.env`, API keys or exchange credentials. Backtests do not guarantee future profitability.
