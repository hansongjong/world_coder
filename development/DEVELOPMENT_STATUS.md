# TG-SYSTEM Enterprise Development Report

**Date**: 2024-05-23
**Architect**: CODER-X
**Version**: 3.1.0 (Phase 3 Complete)

## 1. 프로젝트 개요 (Overview)
본 프로젝트는 **TG_MASTER_DESIGN**의 '서버리스 아키텍처'와 '통합 마스터 DB(V3)' 사상을 기반으로 구축된 **엔터프라이즈 텔레그램 서비스 관리 플랫폼**입니다.
ERP(과금), Legal(증빙), Resource(자산) 관리뿐만 아니라, **캠페인 자동화 및 스케줄링(Automation)**까지 통합된 중앙 제어 커널(Kernel)을 포함합니다.

## 2. 시스템 아키텍처 (Architecture)

### 2.1 Core Kernel (Engine)
- **Event-Driven Dispatcher**: 요청(Request) 시 동적 함수 로드 및 실행.
- **Interceptors**: ERP(Billing) 및 Legal(Audit) 강제화.
- **Scheduler**: 매분 단위로 예약된 캠페인을 감시하고 실행하는 Cron Loop.

### 2.2 Database (Master DB V3)
- **Identity**: `MasterUser`, `Subscription`
- **Catalog**: `FunctionCatalog`
- **Assets**: `TgSession` (세션/프록시), `TargetList` (데이터)
- **Campaigns**: `Campaign` (스케줄링 및 설정), `ExecutionRequest` (실행 큐)
- **Audit**: `AuditLog` (법적 증빙)

### 2.3 Directory Structure
```
src/
├── api/                # FastAPI Gateway
├── core/               # System Kernel, ERP, Scheduler
│   ├── database/       # SQLAlchemy Schemas (V3, Ext, Campaigns)
│   ├── serverless/     # Handler Interfaces
│   └── kernel.py       # Main Dispatcher
├── handlers/           # Serverless Functions
│   ├── auth.py         # Login
│   ├── tg_sender.py    # Sender
│   ├── tg_scraper.py   # Scraper
│   ├── tg_joiner.py    # Joiner
│   ├── session_mgr.py  # Session Validator
│   ├── data_mgr.py     # Data Importer
│   └── campaign_mgr.py # Campaign Dispatcher (Fan-out)
└── main.py             # App Entry Point (API + Scheduler)
```

## 3. 구현된 기능 (Implemented Capabilities)

### 3.1 인프라 및 관리
| 구분 | 기능명 | 상태 | 비고 |
|:---:|:---|:---:|:---|
| **KERNEL** | **V3 Kernel** | ✅ 완료 | ERP/Audit/Dynamic Loading |
| **INFRA** | **Scheduler** | ✅ 완료 | Asyncio Background Task (Cron-like) |
| **API** | **Gateway** | ✅ 완료 | REST API + Swagger UI |

### 3.2 서비스 카탈로그 (Service Catalog)
| Function Code | 기능 설명 | 상태 |
|:---|:---|:---:|
| `FN_AUTH_REQUEST_CODE` | 로그인 인증번호 요청 | ✅ 완료 |
| `FN_AUTH_SUBMIT_CODE` | 인증번호 입력 (세션 생성) | ✅ 완료 |
| `FN_SESSION_VALIDATE` | 세션 유효성/프록시 검사 | ✅ 완료 |
| `FN_DATA_IMPORT` | 타겟 데이터 업로드/파싱 | ✅ 완료 |
| `FN_MSG_SENDER_V1` | 1:1 메시지 전송 (Unit) | ✅ 완료 |
| `FN_GROUP_SCRAPER_V1` | 그룹 멤버 추출 | ✅ 완료 |
| `FN_CHANNEL_JOINER_V1` | 채널 자동 입장 | ✅ 완료 |
| **`FN_CAMPAIGN_DISPATCH`** | **캠페인 분산 실행 (Fan-out)** | **✅ 완료** |

## 4. 실행 및 테스트 (Usage)

### 4.1 설치 및 초기화 (업데이트됨)
```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 데이터베이스 초기화 (순차 실행 필수)
python src/database/init_v3.py           # Core Schema
python src/database/update_v3_phase2.py  # Assets Schema
python src/database/update_v3_phase3.py  # Campaign Schema (NEW)
python src/database/update_catalog.py    # Function Registry

# 3. 서버 실행 (API + Scheduler 동시 구동)
python src/main.py
```

### 4.2 주요 테스트 시나리오
1. **자산 등록**: `FN_DATA_IMPORT`로 타겟 파일 업로드.
2. **캠페인 예약**: DB나 API로 `Campaign` 테이블에 `scheduled_at`을 미래 시간으로 설정하여 Insert.
3. **자동 실행**: 스케줄러가 시간을 감지 -> `FN_CAMPAIGN_DISPATCH` 실행 -> `FN_MSG_SENDER_V1` 다수 생성 및 발송.
4. **결과 확인**: `/v3/audit/{user_id}` 또는 `/v3/status/{req_id}`.

## 5. 향후 계획 (Next Steps)
- **Frontend Dashboard**: `TG_System_Dashboard_KR.html` 구현을 위한 UI 개발 및 API 연동.
- **Containerization**: 핸들러의 Docker 컨테이너 격리 배포 (보안 강화).
- **Advanced Billing**: 단순 차감이 아닌, PG사 연동 및 상세 결제 내역 관리.