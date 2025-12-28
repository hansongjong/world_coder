# World Coder

AI 기반 소프트웨어 개발 자동화 플랫폼

## 프로젝트 개요

World Coder는 AI(LLM)를 활용하여 소프트웨어 설계부터 구현까지 자동화하는 개발 플랫폼입니다.
설계 문서를 분석하고, 고품질 소스 코드를 생성하며, 실제 실행 및 테스트까지 수행합니다.

### 핵심 철학
- **Clean Code** - 읽기 쉽고 유지보수 가능한 코드
- **SOLID 원칙** - 확장 가능한 객체지향 설계
- **보안 최우선** - OWASP 기준 보안 취약점 방지

---

## 프로젝트 구조

```
world_coder/
├── coder.py              # AI 코딩 에이전트 (GUI)
├── config.env            # 환경 설정 (API 키 등)
├── persona.txt           # AI 페르소나 정의
├── instructions.txt      # 개발 지침서
├── tools.txt             # 사용 가능 도구 정의
│
└── development/          # 개발 워크스페이스
    ├── src/              # 백엔드 소스 코드
    │   ├── commerce/     # 커머스/POS 모듈
    │   ├── core/         # 핵심 설정
    │   ├── database/     # DB 엔진
    │   └── main_commerce.py
    │
    ├── tg_pos_app/       # Flutter POS 클라이언트
    │   ├── lib/
    │   │   ├── screens/  # 화면 (14개)
    │   │   ├── services/ # API 서비스
    │   │   ├── widgets/  # 위젯
    │   │   └── l10n/     # 다국어 (한/영)
    │   └── pubspec.yaml
    │
    ├── scripts/          # 유틸리티 스크립트
    ├── docs/             # 설계 문서
    └── tests/            # 테스트 코드
```

---

## 주요 기능

### 1. AI 코딩 에이전트 (`coder.py`)
- Google Gemini API 기반 코드 생성
- 설계 문서 자동 분석 및 구현
- 터미널 명령 실행 (`[CMD_EXEC]`)
- 파일 읽기/쓰기 (`[CODE_READ]`, `[CODE_WRITE]`)

### 2. Smart Universal POS System
멀티테넌트 POS 시스템 - 카페, 음식점, 헬스장, 편의점 등 다양한 업종 지원

#### 백엔드 (FastAPI + SQLite)
| 모듈 | 설명 |
|------|------|
| `commerce/auth` | 2단계 인증 (유저→매장 선택) |
| `commerce/api/products` | 상품/카테고리 관리 |
| `commerce/api/orders` | 주문/결제/환불 처리 |
| `commerce/api/stats` | 매출 통계 (일별/기간별) |
| `commerce/api/store_config` | 매장 설정 관리 |

#### 프론트엔드 (Flutter - Windows/Android/Web)
| 화면 | 설명 |
|------|------|
| `login_screen` | 로그인 |
| `store_selection_screen` | 매장 선택 (멀티테넌트) |
| `pos_screen` | POS 메인 (상품 선택/결제) |
| `payment_modal` | 결제 (카드/현금/할인) |
| `sales_report_screen` | 매출 보고서 (4탭) |
| `order_history_screen` | 주문 내역 |
| `table_map_screen` | 테이블 배치도 |
| `inventory_screen` | 재고 관리 |

---

## 설치 및 실행

### 사전 요구사항
- Python 3.10+
- Flutter 3.0+
- SQLite

### 백엔드 실행
```bash
cd development
pip install -r requirements.txt
PYTHONPATH=. python -m uvicorn src.main_commerce:app --port 8000 --reload
```

### Flutter 앱 실행
```bash
cd development/tg_pos_app
flutter pub get
flutter run -d windows  # 또는 -d chrome, -d android
```

### 테스트 계정
| 계정 | 비밀번호 | 접근 가능 매장 |
|------|---------|--------------|
| boss | 1234 | TG Coffee, TG Korean BBQ |
| cafe | 1234 | TG Coffee Gangnam |
| restaurant | 1234 | TG Korean BBQ |

---

## 기술 스택

### 백엔드
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: SQLite
- **Auth**: JWT (python-jose)
- **Password**: bcrypt

### 프론트엔드
- **Framework**: Flutter 3.x
- **State Management**: Provider
- **HTTP Client**: http package
- **Storage**: SharedPreferences

### AI/자동화
- **LLM**: Google Gemini API
- **GUI**: CustomTkinter

---

## API 문서

백엔드 실행 후 Swagger UI 접속:
```
http://localhost:8000/docs
```

주요 엔드포인트:
- `POST /auth/login` - 로그인
- `POST /auth/select-store` - 매장 선택 + JWT 발급
- `GET /products` - 상품 목록
- `POST /orders` - 주문 생성
- `GET /stats/range` - 기간별 매출 통계

---

## 라이선스

Private Project - All Rights Reserved

---

## 개발자

- **Project**: TG-SYSTEM Enterprise
- **AI Assistant**: Claude Code (Anthropic)
