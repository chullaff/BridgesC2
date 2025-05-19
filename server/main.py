import uvicorn
from fastapi import FastAPI
from .api import router
from .storage import init_db

app = FastAPI(title="BridgesMesh C2 Server")

app.include_router(router, prefix="/api")

if __name__ == "__main__":
    init_db()
    uvicorn.run(app, host="192.168.1.67", port=8000)
