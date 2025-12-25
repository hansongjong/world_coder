# TG-SYSTEM Enterprise Development Report

**Last Updated**: 2024-12-26
**Architect**: CODER-X (Gemini) → Claude (인계)
**Version**: 4.3.0

---

## 1. 프로젝트 개요 (Overview)

본 프로젝트는 **TG_MASTER_DESIGN**의 설계 사양을 기반으로 구축된 **엔터프라이즈 통합 플랫폼**입니다.

### 주요 구성요소
| 구성요소 | 포트 | 설명 |
|---------|------|------|
| **TG-Core** | 8000 | 텔레그램 마케팅/캠페인 엔진 |
| **TG-Commerce** | 8001 | 상거래/POS/주문 관리 |
| **TG-POS App** | - | Flutter 기반 POS 클라이언트 |
| **KDS** | 8001/kds | 주방 디스플레이 시스템 |

---

## 2. 개발 현황 (Development Status)

### Phase 1: Core & Commerce (완료)
| 기능 | 상태 | 비고 |
|-----|------|------|
| Database Schema (V3) | ✅ 완료 | SQLite/SQLAlchemy |
| Auth System (JWT) | ✅ 완료 | bcrypt 해싱 |
| Product/Menu API | ✅ 완료 | |
| Order Engine | ✅ 완료 | |
| Payment (Mock) | ✅ 완료 | |

### Phase 2: Booking & IoT (완료)
| 기능 | 상태 | 비고 |
|-----|------|------|
| Reservation System | ✅ 완료 | 노쇼 방지 로직 |
| IoT Device Control | ✅ 완료 | 가상 장치 시뮬레이터 |
| Queue Management | ✅ 완료 | |

### Phase 3: Automation (완료)
| 기능 | 상태 | 비고 |
|-----|------|------|
| Campaign Scheduler | ✅ 완료 | Cron-like 스케줄러 |
| Message Dispatcher | ✅ 완료 | Fan-out 분산 처리 |
| Telegram Integration | ✅ 완료 | Telethon 기반 |

### Phase 4: Frontend (진행중)
| 기능 | 상태 | 비고 |
|-----|------|------|
| Flutter POS (Windows) | ✅ 완료 | 빌드/실행 확인 |
| Flutter POS (Web) | ⚠️ 부분 | CORS 이슈 해결 필요 |
| KDS (Kitchen Display) | ✅ 완료 | 웹 기반 |
| Admin Dashboard | 🚧 예정 | |

---

## 3. 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                    TG-SYSTEM Enterprise                  │
├─────────────────────────────────────────────────────────┤
│  [Frontend Layer]                                        │
│  ├── Flutter POS App (Windows/Web)                      │
│  ├── KDS Web (Kitchen Display)                          │
│  └── Admin Dashboard (TODO)                             │
├─────────────────────────────────────────────────────────┤
│  [API Gateway Layer]                                     │
│  ├── TG-Core API (Port 8000)                            │
│  │   └── Campaign, Auth, Telegram Handlers              │
│  └── TG-Commerce API (Port 8001)                        │
│      └── Products, Orders, Booking, Membership          │
├─────────────────────────────────────────────────────────┤
│  [Business Logic Layer]                                  │
│  ├── Kernel (ERP/Audit Integration)                     │
│  ├── Scheduler (Campaign Automation)                    │
│  └── Service Handlers (Serverless Functions)            │
├─────────────────────────────────────────────────────────┤
│  [Data Layer]                                            │
│  └── SQLite (tg_master_v3.db)                           │
│      ├── Core Tables (User, Subscription, Audit)        │
│      └── Commerce Tables (Store, Product, Order)        │
└─────────────────────────────────────────────────────────┘
```

---

## 4. 실행 방법

### 빠른 시작 (Windows)
```bash
cd development
run_all.bat
```

### 수동 실행
```bash
# Terminal 1: Core Server (Port 8000)
python src/main.py

# Terminal 2: Commerce Server (Port 8001)
python src/main_commerce.py

# Terminal 3: Flutter POS
cd tg_pos_app && flutter run -d windows
```

### 접속 URL
- **Commerce API Docs**: http://localhost:8001/docs
- **Core API Docs**: http://localhost:8000/docs
- **KDS (Kitchen)**: http://localhost:8001/kds

---

## 5. 개발 히스토리

### Gemini (CODER-X) Phase
- 프로젝트 초기 설계 및 스캐폴딩
- Clean Architecture 적용
- Core/Commerce 백엔드 개발
- Flutter POS 앱 개발

### Claude Phase (2024-12-26~)
- Gemini 작업 인계
- POS 로그인 버그 수정 (seed_data 자동 실행)
- Windows 빌드 이슈 해결 (flutter_secure_storage → shared_preferences)
- 미사용 파일 정리 (pos_screen.dart, pos_screen_v2.dart 삭제)
- 문서 정리 및 현행화

---

## 6. 향후 계획

| 우선순위 | 작업 | 설명 |
|---------|------|------|
| 1 | ERP 매출 리포트 | 일별/월별 매출 집계 API |
| 2 | Admin Dashboard | 웹 기반 관리자 대시보드 |
| 3 | Docker 배포 | 컨테이너화 및 운영 환경 구축 |
| 4 | 사용자 앱 | 손님용 예약/주문 모바일 앱 |

---

## 7. 파일 구조

```
world_coder/
├── coder.py                 # Gemini 연동 개발 도구
├── config.env               # 환경 설정
├── persona.txt              # CODER-X 페르소나
├── instructions.txt         # 개발 지침
├── tools.txt                # 사용 가능 도구
├── tg_pos_app/              # Flutter POS (실행용)
└── development/             # 백엔드 소스
    ├── src/
    │   ├── main.py          # Core Server Entry
    │   ├── main_commerce.py # Commerce Server Entry
    │   ├── core/            # 커널, 스케줄러, 보안
    │   ├── commerce/        # 상거래 도메인
    │   ├── handlers/        # 서버리스 핸들러
    │   └── database/        # DB 엔진 및 마이그레이션
    ├── scripts/             # 유틸리티 스크립트
    ├── tg_pos_app/          # Flutter POS (개발용)
    └── 00_Dev_Logs/         # 개발 히스토리
```
