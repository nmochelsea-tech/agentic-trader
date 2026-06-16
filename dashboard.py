from __future__ import annotations

from pathlib import Path
import pandas as pd

try:
    import streamlit as st
except ImportError as exc:
    raise SystemExit("Streamlit is not installed. Run: pip install streamlit") from exc

ROOT = Path(__file__).resolve().parent
DEFAULT_REPORT_DIR = ROOT / "reports" / "latest"
REQUIRED_REPORTS = [
    "equity_curve.csv",
    "strategy_metrics.csv",
    "benchmark_metrics.csv",
    "trades.csv",
    "parameter_sweep.csv",
    "walk_forward_windows.csv",
    "monte_carlo_summary.csv",
]


def find_report_dir() -> Path:
    candidates = [
        ROOT / "reports" / "latest",
        ROOT / "reports" / "mobile_test",
        ROOT,
    ]
    for c in candidates:
        if (c / "equity_curve.csv").exists() and (c / "strategy_metrics.csv").exists():
            return c
    return ROOT / "reports" / "latest"


def read_csv(report_dir: Path, name: str, **kwargs) -> pd.DataFrame:
    candidates = [report_dir / name, ROOT / name, ROOT / "reports" / "latest" / name, ROOT / "reports" / "mobile_test" / name]
    for path in candidates:
        if path.exists():
            return pd.read_csv(path, **kwargs)
    st.warning(f"Missing {name}. If you uploaded files from iPhone without folders, make sure {name} is uploaded at the top level, then set Report directory to . in the sidebar.")
    return pd.DataFrame()


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
    st.markdown("""
        <style>
        div[data-testid="stMetric"] {background:#161B22;border:1px solid #30363D;padding:.85rem;border-radius:.9rem;}
        div[data-testid="stMetricValue"] {font-size:1.35rem;}
        @media (max-width:768px){.block-container{padding-top:1rem;padding-left:.8rem;padding-right:.8rem;}h1{font-size:1.55rem!important;}h2,h3{font-size:1.1rem!important;}div[data-testid="stMetricValue"]{font-size:1.15rem;}}
        </style>
    """, unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(page_title="Agentic Trader", page_icon="📈", layout="wide")
    render_mobile_css()
    st.title("📈 Agentic Trader")
    st.caption("Mobile-friendly research dashboard for paper performance, risk, and strategy insight. Not financial advice.")

    detected = find_report_dir()
    with st.sidebar:
        st.header("Controls")
        st.success(f"Using report directory: {detected}")
        report_dir = Path(st.text_input("Report directory", str(detected), help="Use . if all CSV files are uploaded at the top level of GitHub."))
        st.markdown("If you uploaded from iPhone and lost folders, this patched version automatically checks the top-level folder too.")

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
    metrics = [("Total Return","total_return",fmt_pct),("CAGR","cagr",fmt_pct),("Sharpe","sharpe",fmt_num),("Max Drawdown","max_drawdown",fmt_pct),("Volatility","volatility",fmt_pct)]
    for col, (label, key, formatter) in zip(cols, metrics):
        col.metric(label, formatter(metric_value(strategy_metrics, key)))

    tab_perf, tab_risk, tab_insights, tab_trades, tab_flow = st.tabs(["Performance", "Risk", "Insights", "Trades", "Flow"])
    with tab_perf:
        st.subheader("Equity curve")
        if not equity.empty and "equity" in equity.columns:
            st.line_chart(equity.set_index(date_col)[["equity"]])
        else: st.info("No equity curve available yet.")
        st.subheader("Benchmark comparison")
        if not benchmark_metrics.empty: st.dataframe(benchmark_metrics, use_container_width=True, hide_index=True)
    with tab_risk:
        st.subheader("Drawdown")
        if not equity.empty and "equity" in equity.columns:
            eq = equity.set_index(date_col)["equity"]
            st.line_chart((eq / eq.cummax() - 1).rename("drawdown"))
        risk_cols = st.columns(3)
        risk_cols[0].metric("Worst drawdown", fmt_pct(metric_value(strategy_metrics,"max_drawdown")))
        risk_cols[1].metric("Sortino", fmt_num(metric_value(strategy_metrics,"sortino")))
        risk_cols[2].metric("Calmar", fmt_num(metric_value(strategy_metrics,"calmar")))
        st.markdown("**Monte Carlo stress test**")
        if not mc_summary.empty: st.dataframe(mc_summary, use_container_width=True, hide_index=True)
    with tab_insights:
        st.subheader("Best strategy settings from parameter sweep")
        if not sweep.empty:
            sort_col = "sharpe" if "sharpe" in sweep.columns else sweep.columns[-1]
            st.dataframe(sweep.sort_values(sort_col, ascending=False).head(10), use_container_width=True, hide_index=True)
        st.subheader("Walk-forward validation")
        if not walk_forward.empty: st.dataframe(walk_forward, use_container_width=True, hide_index=True)
        st.markdown("**Learning rule:** changes should pass backtest → walk-forward → Monte Carlo → paper trading → human approval before deployment.")
    with tab_trades:
        st.subheader("Recent trades")
        if not trades.empty: st.dataframe(trades.tail(50), use_container_width=True, hide_index=True)
    with tab_flow:
        st.subheader("System flowchart")
        for p in [ROOT/"agentic_trader_flowchart.png", ROOT/"docs"/"assets"/"agentic_trader_flowchart.png"]:
            if p.exists():
                st.image(str(p), use_container_width=True)
                break
        else:
            st.info("Flowchart image not found. The dashboard metrics still work.")
        st.markdown("Feedback loop: data → features → signals → risk checks → trades → portfolio results → tests → approved strategy improvements.")

if __name__ == "__main__":
    main()
