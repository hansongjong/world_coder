import sys
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))
TEMPLATES_DIR = BASE_DIR / "src" / "templates"

# API Modules
from src.commerce.api import products, orders, booking, iot, queue, crm, hr, delivery, membership, inventory, stats, store_config, sync
from src.commerce.auth import routes as auth_routes

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

app = FastAPI(title="TG-COMMERCE Platform", version="4.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(auth_routes.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(booking.router)
app.include_router(iot.router)
app.include_router(queue.router)
app.include_router(crm.router)
app.include_router(hr.router)
app.include_router(delivery.router)
app.include_router(membership.router)
app.include_router(inventory.router)
app.include_router(stats.router)
app.include_router(store_config.router)
app.include_router(sync.router)

# [Web Views]
@app.get("/")
def home(request: Request):
    """Web POS"""
    return templates.TemplateResponse("web_pos.html", {"request": request})

@app.get("/kds")
def view_kds(request: Request):
    """[NEW] Kitchen Display System"""
    return templates.TemplateResponse("kds.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("src.main_commerce:app", host="0.0.0.0", port=8001, reload=True)