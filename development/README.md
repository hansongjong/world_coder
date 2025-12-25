# TG-SYSTEM Enterprise Platform

**TG_MASTER_DESIGN** 설계 사양을 기반으로 구축된 엔터프라이즈 통합 플랫폼입니다.

## 시스템 구성

| 구성요소 | 포트 | 설명 |
|---------|------|------|
| TG-Core | 8000 | 텔레그램 마케팅/캠페인 엔진 |
| TG-Commerce | 8001 | 상거래/POS/주문 관리 |
| Flutter POS | - | Windows/Web POS 클라이언트 |
| KDS | 8001/kds | 주방 디스플레이 시스템 |

## 빠른 시작

### Windows (권장)
```bash
run_all.bat
```

### 수동 실행
```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. Core 서버 (Port 8000)
python src/main.py

# 3. Commerce 서버 (Port 8001) - 별도 터미널
python src/main_commerce.py

# 4. Flutter POS - 별도 터미널
cd tg_pos_app && flutter run -d windows
```

## 접속 URL

- **Core API Docs**: http://localhost:8000/docs
- **Commerce API Docs**: http://localhost:8001/docs
- **KDS (주방)**: http://localhost:8001/kds

## 기본 계정

- **ID**: `owner`
- **PW**: `1234`

## 프로젝트 구조

```
development/
├── src/
│   ├── main.py              # Core Server
│   ├── main_commerce.py     # Commerce Server
│   ├── core/                # 커널, 스케줄러, 보안
│   ├── commerce/            # 상거래 도메인
│   ├── handlers/            # 서버리스 핸들러
│   └── database/            # DB 엔진
├── scripts/                 # 유틸리티 스크립트
├── tg_pos_app/              # Flutter POS 앱
└── 00_Dev_Logs/             # 개발 히스토리
```

## 문서

- [DEVELOPMENT_STATUS.md](DEVELOPMENT_STATUS.md) - 개발 현황
- [README_RUN_GUIDE.md](README_RUN_GUIDE.md) - 상세 실행 가이드
- [DESIGN_TRACEABILITY.md](DESIGN_TRACEABILITY.md) - 설계-구현 추적
- [docs/DEVELOPMENT_SEQUENCE.md](docs/DEVELOPMENT_SEQUENCE.md) - 개발 순서

## 개발자

- **Gemini (CODER-X)**: 초기 개발
- **Claude**: 인계 및 유지보수 (2024-12~)
