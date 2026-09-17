from fastapi import FastAPI
app = FastAPI(
    title="GradAtlas API",
    version="0.1.0",
)

@app.get("/")
def root():
    return {
        "name": "GradAtlas",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}