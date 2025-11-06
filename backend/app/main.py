from fastapi import FastAPI
from fastapi.responses import FileResponse
from app.db import init_db
from app.api.dashboard import router as dashboard_router
from app.api.lead import router as lead_router
from app.services.sync_data import sync_data
import time
import threading
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()
init_db()
sync_data()


def loop_sync():
    while True:
        time.sleep(300)
        sync_data()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # aceita requisições de qualquer origem
    allow_credentials=True,
    allow_methods=["*"],  # aceita todos os métodos HTTP
    allow_headers=["*"],  # aceita todos os cabeçalhos
)
threading.Thread(target=loop_sync, daemon=True).start()

app.include_router(dashboard_router)
app.include_router(lead_router)

static = Path("app/static/react")
app.mount("/static", StaticFiles(directory=static), name="static")

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    file_path = static / full_path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    return FileResponse(static / "index.html")