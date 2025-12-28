# World Coder 개발 현황 보고서

> **최종 업데이트**: 2025-12-28 17:00
> **보고자**: WORLD_CODER
> **IRON PROTOCOL 준수**: 매 작업 완료 시 본 문서 업데이트 필수

---

## 1. 현재 Phase 진척률

| Phase | 설명 | 진척률 | 상태 |
|-------|------|--------|------|
| Phase 1 | 핵심 POS 기능 | 95% | 거의 완료 |
| Phase 2 | 멤버십/예약 | 50% | 진행 중 |
| Phase 3 | IoT 연동 | 15% | 일부 시작 |
| Phase 4 | TgMain 연동 | 95% | 거의 완료 |

---

## 2. 최근 완료 작업

### [2025-12-28] 오후 (2차)
- [x] 영수증 API 구현 (receipt.py)
  - JSON 데이터 조회
  - 텍스트 형식 (ESC/POS 프린터용)
  - HTML 형식 (웹/앱 표시용)
- [x] KDS 고도화 (kds.html)
  - 실시간 타이머 (경과시간 표시)
  - 새 주문 알림 + 사운드
  - 상태별 통계 (대기/조리중/완료)
  - 연결 상태 표시
  - 상태 워크플로우 (조리시작 → 완료알림 → 픽업완료)
- [x] 재고 파이프라인 완성
  - ProductRecipe (BOM) 테이블 추가
  - InventoryService 서비스 클래스
  - 주문 시 자동 재고 차감
  - 레시피 관리 API (CRUD)

### [2025-12-28] 오전/오후 (1차)
- [x] sync.py 연동 API 구현 완료
- [x] expected_deliveries, sync_logs 테이블 모델 생성
- [x] WebhookSender 클래스 구현
- [x] HMAC Signature 검증 로직 구현
- [x] ORDER_PAID / ORDER_REFUNDED 이벤트 발송 구현
- [x] STOCK_LOW 이벤트 발송 구현
- [x] MEMBER_CREATED 이벤트 발송 구현
- [x] main_commerce.py에 sync, receipt 라우터 등록

---

## 3. 현재 진행 중 작업

- [ ] 없음

---

## 4. 대기 중인 작업

### 연동 관련
- [ ] Webhook 재전송 큐 구현 (Redis 권장)
- [ ] Timestamp 만료 검증 (5분 이상 된 요청 거부)

### 프로덕션 준비
- [ ] 환경변수 설정 가이드 작성
- [ ] API 통합 테스트 작성
- [ ] PostgreSQL 마이그레이션

### Phase 2 확장
- [ ] 구독 결제 시스템
- [ ] P2P 매칭 완성

---

## 5. 이슈 및 블로커

| ID | 내용 | 심각도 | 상태 |
|----|------|--------|------|
| - | 현재 등록된 이슈 없음 | - | - |

---

## 6. 연동 현황 (World Coder ↔ TgMain)

### 발신 Webhook (World → TgMain)
| 이벤트 | 상태 | 트리거 |
|--------|------|--------|
| ORDER_PAID | [x] 구현됨 | 결제 완료 시 (orders.py) |
| ORDER_REFUNDED | [x] 구현됨 | 환불 시 (orders.py) |
| STOCK_LOW | [x] 구현됨 | 안전재고 미달 시 (inventory.py, orders.py) |
| DELIVERY_RECEIVED | [x] 구현됨 | 입고 확인 시 (sync.py) |
| MEMBER_CREATED | [x] 구현됨 | 신규 회원 가입 시 (membership.py) |

### 수신 API (TgMain → World)
| 엔드포인트 | 상태 | 비고 |
|------------|------|------|
| POST /api/v1/sync/purchase-order | [x] 구현됨 | 발주서 수신 → 입고 예정 |
| POST /api/v1/sync/vendor | [x] 구현됨 | 거래처 동기화 |
| POST /api/v1/sync/inventory-item | [x] 구현됨 | 품목 동기화 |

---

## 7. 핵심 파일 현황

```
development/src/commerce/api/
├── orders.py       ✅ 구현됨 (Webhook 연동 + 재고 자동 차감)
├── products.py     ✅ 구현됨
├── membership.py   ✅ 구현됨 (MEMBER_CREATED 연동)
├── inventory.py    ✅ 구현됨 (STOCK_LOW + 레시피 관리)
├── receipt.py      ✅ NEW - 영수증 API
├── booking.py      ✅ 구현됨
├── iot.py          ✅ 구현됨
└── sync.py         ✅ 구현됨 (TgMain 연동)

development/src/commerce/services/
├── __init__.py           ✅ 생성됨
├── webhook_sender.py     ✅ 구현됨
└── inventory_service.py  ✅ NEW - 재고 서비스

development/src/commerce/domain/
└── models.py       ✅ 구현됨
    - ExpectedDelivery, ExpectedDeliveryItem
    - SyncLog, Vendor
    - ProductRecipe (BOM)

development/src/templates/
└── kds.html        ✅ 고도화됨 (타이머, 알림, 통계)
```

---

## 8. API 엔드포인트 요약

### 영수증 API (/receipt)
- `GET /receipt/{order_id}` - 영수증 데이터 (JSON)
- `GET /receipt/{order_id}/text` - 텍스트 형식
- `GET /receipt/{order_id}/html` - HTML 형식

### 재고 API (/inventory)
- `POST /inventory/update` - 재고 수량 변경
- `GET /inventory/list/{store_id}` - 재고 현황
- `GET /inventory/recipe/{product_id}` - 제품 레시피 조회
- `POST /inventory/recipe` - 레시피 설정
- `DELETE /inventory/recipe/{recipe_id}` - 레시피 삭제

---

**IRON PROTOCOL에 따라 매 작업 완료 시 본 문서를 업데이트해야 합니다.**
