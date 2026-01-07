from fastapi import FastAPI

app = FastAPI(title="AI Crypto Terminal")

@app.get("/")
def root():
    return {"status": "backend running"}
