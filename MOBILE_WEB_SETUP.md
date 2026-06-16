# Mobile Web Setup: Run the Agentic Trader Dashboard from your iPhone

This project is now set up as a phone-friendly web app. The easiest path is:

1. Put this folder in a GitHub repository.
2. Deploy it to Streamlit Community Cloud.
3. Open the Streamlit URL from Safari on your iPhone.
4. Add it to your Home Screen so it feels like an app.

The app is research/paper-trading oriented by default. Do not connect real-money trading until you have tested it extensively and added broker credentials securely.

---

## What you need once

- A computer for the first setup.
- A GitHub account.
- A Streamlit Community Cloud account.
- This project folder.

You do **not** need to run Python directly on your iPhone. Your phone just opens the web dashboard.

---

## Step 1 — Unzip the project

Download and unzip the package. You should see a folder named:

```text
agentic_trader
```

Inside it, important files include:

```text
app.py
 dashboard.py
 requirements.txt
 configs/config.example.yaml
 data/sample_prices.csv
 reports/latest/
 docs/MOBILE_WEB_SETUP.md
```

---

## Step 2 — Create a GitHub repository

1. Go to GitHub.
2. Create a new repository, for example:

```text
agentic-trader-dashboard
```

3. Keep it private if you want.
4. Upload all files from the `agentic_trader` folder.

The top level of the repository should contain `app.py`, `dashboard.py`, and `requirements.txt`.

---

## Step 3 — Deploy on Streamlit Community Cloud

1. Go to Streamlit Community Cloud.
2. Choose **New app**.
3. Pick your GitHub repository.
4. Set the main file path to:

```text
app.py
```

5. Click **Deploy**.

After it finishes, Streamlit gives you a public or private app URL. Open that URL on your iPhone.

---

## Step 4 — Add it to your iPhone Home Screen

1. Open the Streamlit app URL in Safari.
2. Tap the Share button.
3. Tap **Add to Home Screen**.
4. Name it something like:

```text
Trader Dashboard
```

Now you can launch it like a normal app.

---

## Step 5 — Refresh the test results

On your computer, from inside the project folder:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python -m agentic_trader.cli test --config configs/config.example.yaml --out reports/latest
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH="src"
python -m agentic_trader.cli test --config configs/config.example.yaml --out reports/latest
```

Commit and push the updated `reports/latest` files to GitHub. Streamlit will redeploy and your phone dashboard will show the new results.

---

## Step 6 — Make it feel more live

For a true live dashboard, you need an automated job that updates `reports/latest` on a schedule. There are three practical options:

### Option A — Manual refresh, easiest

Run the test command on your computer whenever you want updated results, then push the results.

### Option B — GitHub Actions scheduled refresh

Add a scheduled workflow that runs the test suite and commits the updated reports. This is useful for daily paper-trading style updates.

### Option C — Server deployment

Deploy to a small server that runs the dashboard and scheduled refresh job in the same environment. This is better for real live paper trading, alerts, and broker integrations.

---

## Recommended first setup

Start with this:

```text
Streamlit app + manual report refresh + paper trading only
```

Then upgrade to:

```text
Streamlit app + scheduled report refresh + live market data + alerts
```

Only after that should you consider:

```text
broker connection + real orders + strict human approval
```

---

## Safety rules before real trading

Keep these locked behind manual approval:

- Real-money execution
- Maximum position size
- Leverage
- Options
- Shorting
- Crypto trading
- New symbols
- Strategy parameter changes
- Risk-limit changes

The agent can recommend changes. It should not silently grant itself more freedom.
