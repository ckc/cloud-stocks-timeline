import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.io as pio

# --- Configuration ---
# symbols = ["AKAM", "FSLY", "AMZN", "MSFT", "GOOGL", "NET"]
symbols = ["AKAM", "FSLY", "AMZN", "MSFT", "GOOGL", "NET", "DOCN"]
end = datetime.today()
start = end - timedelta(days=5 * 365)

brand_colors = {
    "AKAM": "#0099CC",   # Akamai blue
    "FSLY": "#FF282D",   # Fastly red
    "AMZN": "#FF9900",   # Amazon orange
    "MSFT": "#737373",   # Neutral gray
    "GOOGL": "#4285F4",  # Google blue
    "NET": "#F38020",    # Cloudflare orange
    "DOCN": "#7B3FE4",   # DigitalOcean purple highlight
}

# --- Download historical prices ---
# data = yf.download(symbols, start=start, end=end)["Adj Close"]
raw = yf.download(symbols, start=start, end=end)
# 如果是多股票，多層欄位：('Close', 'AMZN') 這種
if isinstance(raw.columns, pd.MultiIndex):
    data = raw["Close"]
else:
    # 單股票情況
    data = raw[["Close"]].rename(columns={"Close": symbols[0]})

# --- Example events (add/adjust as you like) ---
events = [
    # Example Akamai events
    dict(symbol="AKAM", date="2022-02-15", label="AKAM earnings beat; guidance raised"),
    dict(symbol="AKAM", date="2023-07-25", label="Akamai security platform update"),
    # Example Fastly events
    dict(symbol="FSLY", date="2020-10-14", label="Fastly warning on customer usage"),
    dict(symbol="FSLY", date="2023-08-02", label="Fastly earnings; edge cloud growth"),
    # Amazon
    dict(symbol="AMZN", date="2022-04-28", label="AMZN Q1 2022 results; AWS strong"),
    dict(symbol="AMZN", date="2023-10-27", label="Prime & AWS drive AMZN rally"),
    # Microsoft
    dict(symbol="MSFT", date="2023-01-23", label="MSFT AI / OpenAI investment news"),
    dict(symbol="MSFT", date="2024-10-24", label="Azure AI growth highlighted"),
    # Alphabet
    dict(symbol="GOOGL", date="2022-02-01", label="GOOGL stock split announcement"),
    dict(symbol="GOOGL", date="2023-10-24", label="Cloud & ads earnings focus"),
    # Cloudflare
    dict(symbol="NET", date="2023-05-05", label="NET earnings; usage-based pricing"),
    dict(symbol="NET", date="2024-02-09", label="Cloudflare security/zero trust push"),
    
    # DOCN - DigitalOcean 重點事件（示例，日期可自行改）
    dict(symbol="DOCN", date="2024-02-24", label="DOCN earnings; focus on AI-native customers"),
    dict(symbol="DOCN", date="2025-11-10", label="DOCN upgraded; price target raised"),
]

# Filter events to price range and ensure dates align
df = data.dropna(how="all")
df_events = []
for ev in events:
    d = pd.to_datetime(ev["date"])
    if d in df.index and ev["symbol"] in df.columns:
        price = df.loc[d, ev["symbol"]]
        df_events.append({**ev, "date": d, "price": price})

# --- Build interactive figure ---
fig = go.Figure()

for sym in symbols:
    if sym not in df.columns:
        continue

    is_docn = (sym == "DOCN")

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df[sym],
            mode="lines",
            name=sym,
            # line=dict(color=brand_colors.get(sym, "#CCCCCC"), width=2),
            line=dict(
                color=brand_colors.get(sym, "#CCCCCC"),
                width=4 if is_docn else 2,
                dash="solid" if is_docn else "dot",
            ),
            hovertemplate=(
                f"<b>{sym}</b><br>"
                "%{x|%Y-%m-%d}<br>"
                "Price: %{y:.2f} USD"
                "<extra></extra>"
            ),
        )
    )

# Add annotations as separate scatter markers
for ev in df_events:
    fig.add_trace(
        go.Scatter(
            x=[ev["date"]],
            y=[ev["price"]],
            mode="markers",
            marker=dict(
                size=10,
                color=brand_colors.get(ev["symbol"], "#FFFFFF"),
                line=dict(width=1, color="#000000"),
                symbol="circle",
            ),
            name=f"{ev['symbol']} event",
            hovertemplate=(
                f"<b>{ev['symbol']}</b><br>"
                f"{ev['label']}<br>"
                "%{x|%Y-%m-%d}<br>"
                "Price: %{y:.2f} USD"
                "<extra></extra>"
            ),
            showlegend=False,
        )
    )

fig.update_layout(
    title="CDN & Cloud Leaders – 5‑Year Stock Timeline",
    xaxis_title="Date",
    yaxis_title="Adjusted Close (USD)",
    hovermode="x unified",
    template="plotly_dark",
    plot_bgcolor="#000000",
    paper_bgcolor="#000000",
    font=dict(color="#FFFFFF", family="Arial, sans-serif"),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        bgcolor="rgba(0,0,0,0.0)",
    ),
)

# Tighten margins for a single‑page look
fig.update_layout(margin=dict(l=60, r=20, t=60, b=60))

html = pio.to_html(
    fig,
    include_plotlyjs="cdn",
    full_html=True,
    default_height="100%",
    default_width="100%",
)

with open("stocks_timeline.html", "w", encoding="utf-8") as f:
    f.write(html)
