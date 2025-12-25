# TG-SYSTEM Execution Guide

본 가이드는 **TG-SYSTEM (Enterprise Platform)**의 설치, 실행, 모니터링 방법을 설명합니다.

## 1. 사전 준비 (Prerequisites)

### 1.1 의존성 패키지 설치
가상환경(venv) 진입 후, 최신 의존성 패키지를 설치하십시오. (Jinja2 등 신규 라이브러리 포함)
```bash
pip install -r requirements.txt
```

### 1.2 데이터베이스 초기화 (최초 1회 필수)
시스템이 사용하는 모든 테이블(V3 Core, Commerce, Gap Features)을 생성합니다.
```bash
# 1. Core & Commerce Base
python src/database/init_v3.py
python src/database/update_commerce_phase2.py

# 2. Additional Features (Phase 2.5 Gap Filling)
python src/database/update_commerce_gap.py
python src/database/update_commerce_gap_v2.py

# 3. Catalog & Data Seeding
python src/database/update_catalog.py
python scripts/seed_commerce_data.py
```

---

## 2. 서버 실행 방법 (How to Run)

### 방법 A: 개발자 모드 (Python 직접 실행)
두 개의 터미널 창을 열고 각각 실행해야 합니다.

**Terminal 1: Core Kernel & Dashboard (Port 8000)**
이 서버가 **대시보드**를 제공합니다.
```bash
python src/main.py
```

**Terminal 2: Commerce Engine (Port 8001)**
POS 및 주문 처리를 담당하는 비즈니스 서버입니다.
```bash
python src/main_commerce.py
```

### 방법 B: 운영 모드 (Docker 원클릭 실행)
Docker가 설치되어 있다면, 배치 파일을 통해 모든 서비스(Core, Commerce, Nginx)를 한 번에 띄웁니다.
```bash
# Windows
start_system.bat

# Linux/Mac
docker-compose up -d --build
```

---

## 3. 대시보드 및 서비스 접속 (Access)

서버가 실행 중이라면 아래 주소로 접속하십시오.

### 📊 통합 운영 대시보드 (Live Ops)
산출물 현황과 시스템 상태를 실시간으로 확인합니다.
*   **URL**: [http://localhost:8000/ops/status](http://localhost:8000/ops/status)

### 🛠️ API 문서 (Swagger UI)
백엔드 기능을 직접 테스트할 수 있습니다.
*   **Core API (Auth/Campaign)**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Commerce API (POS/Booking)**: [http://localhost:8001/docs](http://localhost:8001/docs)

---

## 4. 문제 해결 (Troubleshooting)
*   **ModuleNotFoundError**: `pip install -r requirements.txt`를 다시 실행하십시오.
*   **Port already in use**: 8000번 또는 8001번 포트를 사용하는 다른 프로그램을 종료하십시오.
*   **Database Error**: `db.sqlite3` (또는 `tg_master_v3.db`) 파일을 삭제 후 DB 초기화 스크립트를 재실행하십시오.