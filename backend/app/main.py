from fastapi import FastAPI
from app.db import init_db
from app.api.dashboard import router as dashboard_router
from app.services.sync_data import sync_data
import time
import threading

app = FastAPI()
init_db()
sync_data()

def loop_sync():
    while True:
        time.sleep(300)
        sync_data()
        

threading.Thread(target=loop_sync, daemon=True).start()

app.include_router(dashboard_router)