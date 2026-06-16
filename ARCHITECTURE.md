# Architecture

## Components

1. Market Data Layer
   - Pulls historical daily bars and latest prices.
   - v1 uses CSV to keep the system auditable.

2. Strategy Engine
   - Converts market data into a target symbol.
   - v1 uses ETF trend/momentum rotation.

3. Risk Manager
   - Converts target symbol into a bounded order intent.
   - Enforces max position size, max trade size, and cash reserve.

4. Approval Gate
   - Requires manual approval by default.
   - Production can use notification-based approval.

5. Broker Adapter
   - PaperBroker is included.
   - RobinhoodMCPBroker is intentionally a boundary class; wire this through Robinhood MCP only after you create the agentic account.

6. Ledger/Audit
   - Every fill is written to CSV.
   - Extend this with strategy version, prices, and model prompts before live trading.

## LLM role

Do not let the LLM invent orders. Use the LLM for:
- news summarization
- thesis critique
- risk checklist completion
- explaining why a deterministic signal was produced

Keep order generation deterministic and testable.
