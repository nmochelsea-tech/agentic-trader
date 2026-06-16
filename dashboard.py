from __future__ import annotations

from pathlib import Path
import pandas as pd

try:
    import streamlit as st
except ImportError as exc:
    raise SystemExit("Streamlit is not installed. Run: pip install streamlit") from exc

ROOT = Path(__file__).resolve().parent
DEFAULT_REPORT_DIR = ROOT / "reports" / "latest"


def read_csv(report_dir: Path, name: str, **kwargs) -> pd.DataFrame:
    path = report_dir / name
    if not path.exists():
        st.warning(f"Missing {name}. Run the test command first.")
        return pd.DataFrame()
    return pd.read_csv(path, **kwargs)


def metric_value(df: pd.DataFrame, name: str):
    if df.empty:
        return None
    if name in df.columns and len(df) > 0:
        return df.iloc[0][name]
    lower_cols = {c.lower(): c for c in df.columns}
    if "metric" in lower_cols and "value" in lower_cols:
        mcol = lower_cols["metric"]
        vcol = lower_cols["value"]
        hit = df[df[mcol].astype(str).str.lower() == name.lower()]
        if not hit.empty:
            return hit.iloc[0][vcol]
    return None


def fmt_pct(x):
    try:
        return f"{float(x):.2%}"
    except Exception:
        return "—"


def fmt_num(x):
    try:
        return f"{float(x):.2f}"
    except Exception:
        return "—"


def render_mobile_css() -> None:
    st.markdown(
        """
        <style>
        div[data-testid="stMetric"] {
            background: #161B22;
            border: 1px solid #30363D;
            padding: 0.85rem;
            border-radius: 0.9rem;
        }
        div[data-testid="stMetricValue"] { font-size: 1.35rem; }
        @media (max-width: 768px) {
            .block-container { padding-top: 1rem; padding-left: 0.8rem; padding-right: 0.8rem; }
            h1 { font-size: 1.55rem !important; }
            h2, h3 { font-size: 1.1rem !important; }
            div[data-testid="stMetricValue"] { font-size: 1.15rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="Agentic Trader", page_icon="📈", layout="wide")
    render_mobile_css()

    st.title("📈 Agentic Trader")
    st.caption("Mobile-friendly research dashboard for paper performance, risk, and strategy insight. Not financial advice.")

    with st.sidebar:
        st.header("Controls")
        report_dir = Path(st.text_input("Report directory", str(DEFAULT_REPORT_DIR)))
        auto_refresh = st.toggle("Auto-refresh page", value=False, help="Useful when deployed with scheduled report updates.")
        if auto_refresh:
            st.info("Refresh your browser/app to pull newly generated reports from the server.")
        st.markdown("Run fresh tests locally with:")
        st.code("PYTHONPATH=src python -m agentic_trader.cli test --config configs/config.example.yaml --out reports/latest")

    equity = read_csv(report_dir, "equity_curve.csv")
    strategy_metrics = read_csv(report_dir, "strategy_metrics.csv")
    benchmark_metrics = read_csv(report_dir, "benchmark_metrics.csv")
    trades = read_csv(report_dir, "trades.csv")
    sweep = read_csv(report_dir, "parameter_sweep.csv")
    walk_forward = read_csv(report_dir, "walk_forward_windows.csv")
    mc_summary = read_csv(report_dir, "monte_carlo_summary.csv")

    if not equity.empty:
        date_col = "date" if "date" in equity.columns else equity.columns[0]
        equity[date_col] = pd.to_datetime(equity[date_col], errors="coerce")
        equity = equity.sort_values(date_col)
    else:
        date_col = "date"

    st.subheader("Performance snapshot")
    cols = st.columns(5)
    metrics = [
        ("Total Return", "total_return", fmt_pct),
        ("CAGR", "cagr", fmt_pct),
        ("Sharpe", "sharpe", fmt_num),
        ("Max Drawdown", "max_drawdown", fmt_pct),
        ("Volatility", "volatility", fmt_pct),
    ]
    for col, (label, key, formatter) in zip(cols, metrics):
        col.metric(label, formatter(metric_value(strategy_metrics, key)))

    tab_perf, tab_risk, tab_insights, tab_trades, tab_flow = st.tabs([
        "Performance", "Risk", "Insights", "Trades", "Flow"
    ])

    with tab_perf:
        st.subheader("Equity curve")
        if not equity.empty and "equity" in equity.columns:
            st.line_chart(equity.set_index(date_col)[["equity"]])
        else:
            st.info("No equity curve available yet.")

        st.subheader("Benchmark comparison")
        if not benchmark_metrics.empty:
            st.dataframe(benchmark_metrics, use_container_width=True, hide_index=True)
        else:
            st.info("No benchmark metrics found.")

    with tab_risk:
        st.subheader("Drawdown")
        if not equity.empty and "equity" in equity.columns:
            eq = equity.set_index(date_col)["equity"]
            dd = eq / eq.cummax() - 1
            st.line_chart(dd.rename("drawdown"))
        risk_cols = st.columns(3)
        risk_cols[0].metric("Worst drawdown", fmt_pct(metric_value(strategy_metrics, "max_drawdown")))
        risk_cols[1].metric("Sortino", fmt_num(metric_value(strategy_metrics, "sortino")))
        risk_cols[2].metric("Calmar", fmt_num(metric_value(strategy_metrics, "calmar")))

        st.markdown("**Monte Carlo stress test**")
        if not mc_summary.empty:
            st.dataframe(mc_summary, use_container_width=True, hide_index=True)
        else:
            st.info("No Monte Carlo output found.")

    with tab_insights:
        st.subheader("Best strategy settings from parameter sweep")
        if not sweep.empty:
            sort_col = "sharpe" if "sharpe" in sweep.columns else sweep.columns[-1]
            st.dataframe(sweep.sort_values(sort_col, ascending=False).head(10), use_container_width=True, hide_index=True)
        else:
            st.info("No parameter sweep found.")

        st.subheader("Walk-forward validation")
        if not walk_forward.empty:
            st.dataframe(walk_forward, use_container_width=True, hide_index=True)
        else:
            st.info("No walk-forward output found.")

        st.markdown(
            """
            **Learning rule:** the agent may recommend improvements, but strategy/risk changes should be promoted only after
            backtest → walk-forward → Monte Carlo → paper-trading validation → human approval.
            """
        )

    with tab_trades:
        st.subheader("Recent trades")
        if not trades.empty:
            st.dataframe(trades.tail(50), use_container_width=True, hide_index=True)
        else:
            st.info("No trades found.")

    with tab_flow:
        st.subheader("System flowchart")
        flowchart = ROOT / "docs" / "assets" / "agentic_trader_flowchart.png"
        if flowchart.exists():
            st.image(str(flowchart), use_container_width=True)
        st.markdown(
            """
            **Feedback loop:** market data creates features, features create signals, signals pass through risk checks,
            trades update the portfolio, results feed testing, and only validated improvements are promoted back into the strategy.
            """
        )


if __name__ == "__main__":
    main()
