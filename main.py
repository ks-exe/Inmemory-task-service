from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root() -> dict[str, object]:
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
