# World Coder 개발 현황 보고서

> **최종 업데이트**: 2025-12-28 19:00
> **보고자**: WORLD_CODER
> **IRON PROTOCOL 준수**: 매 작업 완료 시 본 문서 업데이트 필수

---

## 1. 현재 Phase 진척률

| Phase | 설명 | 진척률 | 상태 |
|-------|------|--------|------|
| Phase 1 | 핵심 POS 기능 | 98% | 거의 완료 |
| Phase 2 | 멤버십/예약 | 50% | 진행 중 |
| Phase 3 | IoT 연동 | 15% | 일부 시작 |
| Phase 4 | TgMain 연동 | 95% | 거의 완료 |

---

## 2. 최근 완료 작업

### [2025-12-28] 오후 (4차) - 로컬 서버 아키텍처 (CN-2025-12-28-001)
- [x] GENESIS_PLANNER 검토 완료 및 승인
- [x] POS 로컬 서버 구현 (`local_server.dart`)
  - shelf 패키지 기반 HTTP 서버
  - WebSocket 브로드캐스트 지원
  - KDS/키오스크/테이블오더 연결용
- [x] 동기화 서비스 구현 (`sync_service.dart`)
  - lastSyncAt 기반 증분 동기화
  - 오프라인 큐 관리
  - 온라인 복구 시 자동 푸시
- [x] KDS MODE 추가 (`config.js`)
  - `local` 모드: POS 직접 연결
  - `cloud` 모드: 중앙 서버 연결
  - WebSocket URL 자동 결정

### [2025-12-28] 오후 (3차) - 아키텍처 재구성
- [x] 프론트엔드 폴더 분리 (Cloudflare Pages 배포용)
- [x] SYSTEM_ARCHITECTURE.md 작성
- [x] 각 프론트엔드에 config.js 추가

### [2025-12-28] 오후 (2차)
- [x] 영수증 API 구현 (receipt.py)
- [x] KDS 고도화 (kds.html)
- [x] 재고 파이프라인 완성 (BOM)

### [2025-12-28] 오전/오후 (1차)
- [x] sync.py 연동 API 구현 완료
- [x] WebhookSender 클래스 구현
- [x] 모든 Webhook 이벤트 발송 구현

---

## 3. 현재 진행 중 작업

- [ ] 없음

---

## 4. 대기 중인 작업

### POS 로컬 서버 연동
- [ ] Flutter main.dart에 LocalServer 통합
- [ ] KDS index.html에 WebSocket 연결 로직 추가
- [ ] 키오스크/테이블오더 웹 생성

### 프로덕션 배포 준비
- [ ] AWS Lambda 마이그레이션 (SQLAlchemy → DynamoDB)
- [ ] Cloudflare Pages 배포 설정

### Phase 2 확장
- [ ] 구독 결제 시스템
- [ ] P2P 매칭 완성

---

## 5. 이슈 및 블로커

| ID | 내용 | 심각도 | 상태 |
|----|------|--------|------|
| - | 현재 등록된 이슈 없음 | - | - |

---

## 6. 프로젝트 구조

```
world_coder/
├── development/              # Backend (FastAPI - 개발용)
│   └── src/commerce/
│       ├── api/              # REST API endpoints
│       ├── auth/             # Authentication
│       ├── domain/           # Models
│       └── services/         # Business logic
│
├── tg_pos_app/               # Flutter App (POS + 로컬 서버)
│   └── lib/services/
│       ├── local_server.dart # KDS/키오스크 연결용 HTTP 서버
│       └── sync_service.dart # 오프라인→온라인 동기화
│
├── tg_admin_web/             # Admin Dashboard (Cloudflare Pages)
├── tg_kds_web/               # Kitchen Display (local/cloud 모드)
├── tg_web_pos/               # Web POS (백업용)
│
├── SYSTEM_ARCHITECTURE.md
├── INTEGRATION_GUIDE.md
└── PROGRESS_STATUS.md
```

---

## 7. 매장 내부망 아키텍처 (확정)

```
┌─────────────────────────────────────────────────────┐
│                   매장 내부망 (LAN)                  │
│                                                     │
│      ┌──────────────────┐                           │
│      │  POS (로컬 서버)  │◄──────────────────────┐  │
│      │  tg_pos_app      │                        │  │
│      │  :8080           │                        │  │
│      └────────┬─────────┘                        │  │
│               │                                  │  │
│    ┌──────────┼──────────┬───────────┐          │  │
│    ▼          ▼          ▼           ▼          │  │
│  ┌────┐   ┌────────┐  ┌────────┐  ┌────────┐   │  │
│  │KDS │   │키오스크│  │테이블  │  │테이블  │   │  │
│  │주방│   │입구    │  │오더 1  │  │오더 2  │...│  │
│  └────┘   └────────┘  └────────┘  └────────┘   │  │
└─────────────────────────────────────────────────────┘
                    │
                    ▼ (온라인 시에만)
           ┌────────────────┐
           │  AWS 중앙서버   │ ← 결제/정산/동기화만
           └────────────────┘
```

**핵심 원칙**:
- POS = 로컬 서버 (중앙서버 의존 X)
- KDS/키오스크/테이블오더 = POS 클라이언트
- 중앙서버 = 결제/정산/동기화만

---

## 8. API 엔드포인트 요약

| Prefix | Description |
|--------|-------------|
| `/auth` | 인증 (로그인, 토큰) |
| `/products` | 상품 관리 |
| `/orders` | 주문 처리 |
| `/inventory` | 재고 관리 |
| `/stats` | 매출 통계 |
| `/membership` | 멤버십/포인트 |
| `/store` | 매장 설정 |
| `/sync` | TgMain 연동 |
| `/receipt` | 영수증 |

---

**IRON PROTOCOL에 따라 매 작업 완료 시 본 문서를 업데이트해야 합니다.**
