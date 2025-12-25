import sys
import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates # 템플릿 엔진
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import uvicorn

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))
TEMPLATES_DIR = BASE_DIR / "src" / "templates" # 템플릿 경로

from src.core.config import settings
from src.api.routes_v3 import router as v3_router
from src.api.routes_dashboard import router as dashboard_router
from src.api.routes_report import router as report_router
from src.core.scheduler import run_scheduler

# 템플릿 초기화
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler_task = asyncio.create_task(run_scheduler())
    yield
    scheduler_task.cancel()
    try: await scheduler_task
    except asyncio.CancelledError: pass

app = FastAPI(title="TG-SYSTEM Enterprise", version="4.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v3_router)
app.include_router(dashboard_router)
app.include_router(report_router)

# [FIX] 루트 접속 시 JSON 대신 HTML 대시보드 반환
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index_core.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)