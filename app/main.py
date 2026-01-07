from fastapi import FastAPI, Query
import requests
import pandas as pd
import ta

app = FastAPI()

BINANCE_URL = "https://api.binance.com/api/v3/klines"

@app.get("/")
def root():
    return {"status": "backend running"}

@app.get("/signal")
def get_signal(
    symbol: str = Query("BTCUSDT"),
    interval: str = Query("15m"),
    limit: int = Query(100)
):
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    data = requests.get(BINANCE_URL, params=params).json()

    df = pd.DataFrame(data, columns=[
        "open_time","open","high","low","close","volume",
        "close_time","qav","num_trades","taker_base","taker_quote","ignore"
    ])

    df["close"] = df["close"].astype(float)

    # Indikatoriai
    df["ema50"] = ta.trend.ema_indicator(df["close"], window=50)
    df["ema200"] = ta.trend.ema_indicator(df["close"], window=200)
    df["rsi"] = ta.momentum.rsi(df["close"])
    macd = ta.trend.MACD(df["close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()

    last = df.iloc[-1]

    score = 0

    trend = "neutral"
    if last["ema50"] > last["ema200"]:
        trend = "bullish"
        score += 1
    elif last["ema50"] < last["ema200"]:
        trend = "bearish"
        score += 1

    if last["rsi"] < 70 and trend == "bullish":
        score += 1
    if last["rsi"] > 30 and trend == "bearish":
        score += 1

    if last["macd"] > last["macd_signal"]:
        score += 1

    signal = "WAIT"
    if score >= 3 and trend == "bullish":
        signal = "LONG"
    elif score >= 3 and trend == "bearish":
        signal = "SHORT"

    confidence = int((score / 4) * 100)

    return {
        "symbol": symbol,
        "interval": interval,
        "trend": trend,
        "signal": signal,
        "confidence": confidence
    }
