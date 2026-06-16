from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

from .config import TraderConfig
from .data import load_prices, price_matrix
from .strategy import TrendRotationStrategy
from .broker import PaperBroker
from .risk import RiskManager
from .backtest import run_backtest, save_backtest_result
from .sweep import parameter_sweep
from .monte_carlo import bootstrap_returns, summarize_monte_carlo
from .walk_forward import walk_forward_test
from .report import plot_equity, plot_drawdown, write_markdown_report


def build_strategy(cfg):
    return TrendRotationStrategy(
        universe=cfg.universe,
        defensive_symbol=cfg.defensive_symbol,
        fast_ma=cfg.fast_ma,
        slow_ma=cfg.slow_ma,
        momentum_lookback=cfg.momentum_lookback,
    )


def run_live_like(args):
    cfg = TraderConfig.from_yaml(args.config)
    prices = load_prices(args.prices or cfg.price_csv)
    px = price_matrix(prices)
    strategy = build_strategy(cfg)
    signal = strategy.generate_signal(px[cfg.universe])
    risk = RiskManager(max_position_pct=cfg.max_position_pct, max_daily_loss_pct=cfg.max_daily_loss_pct)
    broker = PaperBroker(initial_cash=cfg.initial_cash)
    orders = risk.target_allocation_to_orders(signal.target_symbol, cfg.max_position_pct, broker.portfolio_value(), px.iloc[-1].to_dict())
    for order in orders:
        broker.submit_order(order)
    print(f"Signal as of {signal.as_of}: {signal.target_symbol} — {signal.reason}")
    print("Orders:")
    for order in orders:
        print(order)


def run_tests(args):
    cfg = TraderConfig.from_yaml(args.config)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    prices = load_prices(args.prices or cfg.price_csv)
    px = price_matrix(prices)[cfg.universe]
    strategy = build_strategy(cfg)
    result = run_backtest(px, strategy, cfg.initial_cash, transaction_cost_bps=args.cost_bps)
    save_backtest_result(result, out_dir)
    plot_equity(result.equity, out_dir)
    plot_drawdown(result.equity, out_dir)

    sweep = parameter_sweep(
        px, cfg.universe, cfg.defensive_symbol,
        fast_ma_values=args.fast_ma,
        slow_ma_values=args.slow_ma,
        momentum_values=args.momentum,
        initial_cash=cfg.initial_cash,
    )
    sweep.to_csv(out_dir / "parameter_sweep.csv", index=False)

    mc = bootstrap_returns(result.equity["equity"], simulations=args.simulations, seed=args.seed)
    mc.to_csv(out_dir / "monte_carlo.csv", index=False)
    mc_summary = summarize_monte_carlo(mc)
    mc_summary.to_csv(out_dir / "monte_carlo_summary.csv", index=False)

    wf_windows, wf_equity = walk_forward_test(
        px, cfg.universe, cfg.defensive_symbol,
        fast_ma_values=args.fast_ma,
        slow_ma_values=args.slow_ma,
        momentum_values=args.momentum,
        initial_cash=cfg.initial_cash,
    )
    wf_windows.to_csv(out_dir / "walk_forward_windows.csv", index=False)
    if not wf_equity.empty:
        wf_equity.to_csv(out_dir / "walk_forward_equity.csv")

    report = write_markdown_report(out_dir, result.metrics, result.benchmark_metrics, sweep=sweep, mc_summary=mc_summary)
    print(f"Wrote test artifacts to {out_dir}")
    print(f"Open report: {report}")


def main():
    parser = argparse.ArgumentParser(description="Agentic Trader CLI")
    sub = parser.add_subparsers(dest="command")

    live = sub.add_parser("signal", help="Generate current signal and paper orders")
    live.add_argument("--config", required=True)
    live.add_argument("--prices")
    live.set_defaults(func=run_live_like)

    test = sub.add_parser("test", help="Run backtest, sweep, Monte Carlo, and walk-forward reports")
    test.add_argument("--config", required=True)
    test.add_argument("--prices")
    test.add_argument("--out", default="reports/latest")
    test.add_argument("--cost-bps", type=float, default=2.0)
    test.add_argument("--simulations", type=int, default=500)
    test.add_argument("--seed", type=int, default=7)
    test.add_argument("--fast-ma", nargs="+", type=int, default=[20, 50])
    test.add_argument("--slow-ma", nargs="+", type=int, default=[100, 150, 200])
    test.add_argument("--momentum", nargs="+", type=int, default=[60, 90, 120])
    test.set_defaults(func=run_tests)

    # Backward compatible default: old invocation behaves like signal.
    parser.add_argument("--config", dest="legacy_config")
    parser.add_argument("--paper", action="store_true")
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    elif args.legacy_config:
        args.config = args.legacy_config
        args.prices = None
        run_live_like(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
