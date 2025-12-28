# World Coder 개발 현황 보고서

> **최종 업데이트**: 2025-12-28 16:00
> **보고자**: WORLD_CODER
> **IRON PROTOCOL 준수**: 매 작업 완료 시 본 문서 업데이트 필수

---

## 1. 현재 Phase 진척률

| Phase | 설명 | 진척률 | 상태 |
|-------|------|--------|------|
| Phase 1 | 핵심 POS 기능 | 85% | 진행 중 |
| Phase 2 | 멤버십/예약 | 50% | 진행 중 |
| Phase 3 | IoT 연동 | 15% | 일부 시작 |
| Phase 4 | TgMain 연동 | 95% | 거의 완료 |

---

## 2. 최근 완료 작업

### [2025-12-28] 오후
- [x] STOCK_LOW 이벤트 발송 구현 (inventory.py)
- [x] MEMBER_CREATED 이벤트 발송 구현 (membership.py)

### [2025-12-28] 오전
- [x] sync.py 연동 API 구현 완료
- [x] expected_deliveries, sync_logs 테이블 모델 생성
- [x] WebhookSender 클래스 구현
- [x] HMAC Signature 검증 로직 구현
- [x] ORDER_PAID / ORDER_REFUNDED 이벤트 발송 구현
- [x] main_commerce.py에 sync 라우터 등록
- [x] tg_pos_app 소스 통합 (root → development)

### [이전 작업]
- [x] 주문 API 기본 구현 (orders.py)
- [x] 상품 API 기본 구현 (products.py)
- [x] 멤버십 API 기본 구현 (membership.py)
- [x] 예약 API 기본 구현 (booking.py)
- [x] IoT API 기본 구현 (iot.py)

---

## 3. 현재 진행 중 작업

- [ ] 없음 (TgMain 연동 기본 구현 완료)

---

## 4. 대기 중인 작업

### 연동 관련
- [ ] Webhook 재전송 큐 구현 (Redis 권장)
- [ ] Timestamp 만료 검증 (5분 이상 된 요청 거부)

### POS 기능
- [ ] KDS 고도화
- [ ] 영수증 출력 기능

### 프로덕션 준비
- [ ] 환경변수 설정 가이드 작성
- [ ] API 통합 테스트 작성

---

## 5. 이슈 및 블로커

### 이슈 목록
| ID | 내용 | 심각도 | 상태 |
|----|------|--------|------|
| - | 현재 등록된 이슈 없음 | - | - |

### 블로커
- [ ] 없음

---

## 6. 대기 중인 설계 변경

| 변경 ID | 등급 | 내용 | 상태 |
|---------|------|------|------|
| - | - | 현재 대기 중인 변경 없음 | - |

---

## 7. 연동 현황 (World Coder ↔ TgMain)

### 발신 Webhook (World → TgMain)
| 이벤트 | 상태 | 트리거 |
|--------|------|--------|
| ORDER_PAID | [x] 구현됨 | 결제 완료 시 (orders.py) |
| ORDER_REFUNDED | [x] 구현됨 | 환불 시 (orders.py) |
| STOCK_LOW | [x] 구현됨 | 안전재고 미달 시 (inventory.py) |
| DELIVERY_RECEIVED | [x] 구현됨 | 입고 확인 시 (sync.py) |
| MEMBER_CREATED | [x] 구현됨 | 신규 회원 가입 시 (membership.py) |

### 수신 API (TgMain → World)
| 엔드포인트 | 상태 | 비고 |
|------------|------|------|
| POST /api/v1/sync/purchase-order | [x] 구현됨 | 발주서 수신 → 입고 예정 |
| POST /api/v1/sync/vendor | [x] 구현됨 | 거래처 동기화 |
| POST /api/v1/sync/inventory-item | [x] 구현됨 | 품목 동기화 |

### 입고 예정 관리 API
| 엔드포인트 | 상태 | 비고 |
|------------|------|------|
| GET /api/v1/sync/deliveries | [x] 구현됨 | 입고 예정 목록 |
| GET /api/v1/sync/deliveries/{id} | [x] 구현됨 | 입고 예정 상세 |
| POST /api/v1/sync/deliveries/{id}/receive | [x] 구현됨 | 입고 확인 처리 |
| GET /api/v1/sync/logs | [x] 구현됨 | 동기화 로그 조회 |

### 인증 체계
| 항목 | 상태 |
|------|------|
| API Key 관리 | [x] 구현됨 |
| HMAC-SHA256 Signature 생성 | [x] 구현됨 |
| HMAC-SHA256 Signature 검증 | [x] 구현됨 |
| Timestamp 검증 | [ ] 미구현 (5분 만료 체크) |

---

## 8. 핵심 파일 현황

```
development/src/commerce/api/
├── orders.py       ✅ 구현됨 (ORDER_PAID, ORDER_REFUNDED 연동)
├── products.py     ✅ 구현됨
├── membership.py   ✅ 구현됨 (MEMBER_CREATED 연동)
├── inventory.py    ✅ 구현됨 (STOCK_LOW 연동)
├── booking.py      ✅ 구현됨
├── iot.py          ✅ 구현됨
└── sync.py         ✅ 구현됨 (TgMain 연동, DELIVERY_RECEIVED)

development/src/commerce/services/
├── __init__.py     ✅ 생성됨
└── webhook_sender.py ✅ 구현됨

development/src/commerce/domain/
└── models.py       ✅ 구현됨 (연동 모델 추가 완료)
    - ExpectedDelivery, ExpectedDeliveryItem
    - SyncLog, Vendor
```

---

## 9. GENESIS_PLANNER에 요청 사항

- [ ] 없음

---

**IRON PROTOCOL에 따라 매 작업 완료 시 본 문서를 업데이트해야 합니다.**
