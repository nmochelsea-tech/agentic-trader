from __future__ import annotations

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def _pct(x: float) -> str:
    return f"{x:.2%}"


def plot_equity(equity: pd.DataFrame, out_dir: Path) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5))
    equity["equity"].plot(ax=ax, label="Strategy")
    if "benchmark" in equity.columns:
        equity["benchmark"].plot(ax=ax, label="Benchmark")
    ax.set_title("Equity Curve")
    ax.set_ylabel("Portfolio value")
    ax.legend()
    path = out_dir / "equity_curve.png"
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def plot_drawdown(equity: pd.DataFrame, out_dir: Path) -> Path:
    dd = equity["equity"] / equity["equity"].cummax() - 1
    fig, ax = plt.subplots(figsize=(10, 4))
    dd.plot(ax=ax)
    ax.set_title("Strategy Drawdown")
    ax.set_ylabel("Drawdown")
    path = out_dir / "drawdown.png"
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def write_markdown_report(out_dir: str | Path, metrics: dict, benchmark_metrics: dict, sweep: pd.DataFrame | None = None, mc_summary: pd.DataFrame | None = None) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    lines = ["# Agentic Trader Test Report", "", "## Strategy vs Benchmark", "", "| Metric | Strategy | Benchmark |", "|---|---:|---:|"]
    for key in ["total_return", "cagr", "annualized_volatility", "sharpe", "sortino", "max_drawdown", "calmar"]:
        sv = metrics.get(key, 0)
        bv = benchmark_metrics.get(key, 0)
        if key in {"sharpe", "sortino", "calmar"}:
            lines.append(f"| {key} | {sv:.2f} | {bv:.2f} |")
        else:
            lines.append(f"| {key} | {_pct(sv)} | {_pct(bv)} |")
    lines += ["", f"Trades: {int(metrics.get('num_trades', 0))}", "", "![Equity curve](equity_curve.png)", "", "![Drawdown](drawdown.png)", ""]
    if sweep is not None and not sweep.empty:
        lines += ["## Top Parameter Sets", "", sweep.head(10).to_markdown(index=False), ""]
    if mc_summary is not None and not mc_summary.empty:
        lines += ["## Monte Carlo Bootstrap Summary", "", mc_summary.to_markdown(index=False), ""]
    lines += ["## Notes", "", "This test harness is for research only. It does not prove future profitability and does not account for every real-world execution issue."]
    path = out / "REPORT.md"
    path.write_text("\n".join(lines))
    return path
