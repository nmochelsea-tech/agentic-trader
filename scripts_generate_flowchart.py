from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path('docs/assets')
OUT.mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(18, 11))
ax.set_xlim(0, 18)
ax.set_ylim(0, 11)
ax.axis('off')

def box(x, y, w, h, title, body):
    patch = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.025,rounding_size=0.12', linewidth=1.8, facecolor='white', edgecolor='black')
    ax.add_patch(patch)
    ax.text(x+w/2, y+h-0.28, title, ha='center', va='top', fontsize=13, fontweight='bold')
    ax.text(x+w/2, y+h-0.75, body, ha='center', va='top', fontsize=10, linespacing=1.25)
    return (x, y, w, h)

def arrow(a, b, text=None, rad=0):
    x1, y1, w1, h1 = a
    x2, y2, w2, h2 = b
    start = (x1+w1, y1+h1/2) if x2 > x1 else (x1, y1+h1/2)
    end = (x2, y2+h2/2) if x2 > x1 else (x2+w2, y2+h2/2)
    arr = FancyArrowPatch(start, end, arrowstyle='-|>', mutation_scale=15, linewidth=1.4, color='black', connectionstyle=f'arc3,rad={rad}')
    ax.add_patch(arr)
    if text:
        ax.text((start[0]+end[0])/2, (start[1]+end[1])/2+0.25, text, ha='center', va='center', fontsize=9)

def down_arrow(a, b, text=None):
    x1, y1, w1, h1 = a
    x2, y2, w2, h2 = b
    start = (x1+w1/2, y1)
    end = (x2+w2/2, y2+h2)
    arr = FancyArrowPatch(start, end, arrowstyle='-|>', mutation_scale=15, linewidth=1.4, color='black')
    ax.add_patch(arr)
    if text:
        ax.text((start[0]+end[0])/2+0.25, (start[1]+end[1])/2, text, fontsize=9)

# Trading row
b1 = box(0.5, 8.4, 2.5, 1.45, '1. Market Data', 'Inputs:\nprices, volume, benchmarks\nOutput: clean price feed')
b2 = box(3.5, 8.4, 2.5, 1.45, '2. Data Layer', 'align dates\nfill gaps\nnormalize returns')
b3 = box(6.5, 8.4, 2.5, 1.45, '3. Feature Engine', 'momentum\nvolatility\ndrawdown\ntrend regime')
b4 = box(9.5, 8.4, 2.5, 1.45, '4. Strategy Agent', 'risk-on/risk-off ETF rotation\nOutput: target allocation')
b5 = box(12.5, 8.4, 2.5, 1.45, '5. Risk Manager', 'position caps\ndrawdown guardrails\ncash buffer')
b6 = box(15.5, 8.4, 2.0, 1.45, '6. Broker', 'paper now\nRobinhood adapter later\nOutput: fills')
for a,b in [(b1,b2),(b2,b3),(b3,b4),(b4,b5),(b5,b6)]: arrow(a,b)

ledger = box(12.7, 6.25, 2.9, 1.35, 'Portfolio Ledger', 'positions, cash, trades, fees\nequity curve')
metrics = box(9.2, 6.25, 2.9, 1.35, 'Performance Analyzer', 'CAGR, Sharpe, Sortino\nmax drawdown, win rate')
tests = box(5.7, 6.25, 2.9, 1.35, 'Testing Ecosystem', 'backtest\nwalk-forward\nMonte Carlo\nparameter sweep')
research = box(2.2, 6.25, 2.9, 1.35, 'Research Memory', 'all runs + configs\nwinning/losing regimes\nexperiment log')
optimizer = box(2.2, 3.95, 2.9, 1.35, 'Optimizer Agent', 'suggest parameter/rule changes\nrank candidates by robustness')
review = box(6.6, 3.95, 2.9, 1.35, 'Human Review Gate', 'approve/reject changes\nset risk limits\nprevent overfitting')
deploy = box(11.0, 3.95, 2.9, 1.35, 'Promotion Layer', 'paper deploy first\nthen limited live capital\nversioned configs')
insights = box(14.5, 3.95, 2.7, 1.35, 'Dashboard', 'live metrics\nrisk alerts\ninsights + reports')

# vertical and reverse flow
down_arrow(b6, ledger, 'fills')
arrow(ledger, metrics)
arrow(metrics, tests)
arrow(tests, research)
down_arrow(research, optimizer, 'learn')
arrow(optimizer, review)
arrow(review, deploy)
arrow(deploy, insights)
# feedback to strategy/feature engine: use curved arrows
arr = FancyArrowPatch((12.4, 4.65), (7.75, 8.35), arrowstyle='-|>', mutation_scale=16, linewidth=1.7, color='black', connectionstyle='arc3,rad=-0.35')
ax.add_patch(arr)
ax.text(10.4, 6.0, 'approved improvements\nupdate config/features', ha='center', fontsize=10, fontweight='bold')
# dashboard monitors ledger and metrics
arr2 = FancyArrowPatch((14.5, 4.6), (14.15, 6.25), arrowstyle='-|>', mutation_scale=14, linewidth=1.2, color='black', connectionstyle='arc3,rad=0.1')
ax.add_patch(arr2)
ax.text(15.6, 5.65, 'reads latest\nCSV/DB state', ha='center', fontsize=9)

ax.text(9, 10.55, 'Agentic Trader Architecture + Learning Feedback Loop', ha='center', fontsize=22, fontweight='bold')
ax.text(9, 10.1, 'Safe improvement path: observe → test → stress test → approve → deploy. The bot does not blindly rewrite live risk rules.', ha='center', fontsize=12)
ax.text(0.6, 0.55, 'Safety boundary: live execution, leverage, options, allowed assets, and max drawdown limits require explicit human approval.', fontsize=11, fontweight='bold')

fig.tight_layout()
fig.savefig(OUT / 'agentic_trader_flowchart.png', dpi=200, bbox_inches='tight')
fig.savefig(OUT / 'agentic_trader_flowchart.svg', bbox_inches='tight')
print(OUT / 'agentic_trader_flowchart.png')
