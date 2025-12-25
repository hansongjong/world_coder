# TG-POS App (Flutter)

TG-SYSTEM Commerce 플랫폼용 **POS(Point of Sale) 클라이언트** 애플리케이션입니다.

## 개요

- **플랫폼**: Windows Desktop, Web (Chrome)
- **프레임워크**: Flutter 3.x
- **백엔드**: TG-Commerce API (Port 8001)

## 기능

| 기능 | 설명 | 상태 |
|-----|------|------|
| 로그인 | 점주/직원 인증 | ✅ |
| 메뉴 조회 | 카테고리별 상품 목록 | ✅ |
| 장바구니 | 상품 추가/삭제 | ✅ |
| 주문 생성 | 주문 API 연동 | ✅ |
| 결제 처리 | 결제 모달 (Mock) | ✅ |
| 영수증 출력 | 영수증 다이얼로그 | ✅ |
| 예약 조회 | 예약 목록 확인 | ✅ |

## 프로젝트 구조

```
lib/
├── main.dart              # 앱 진입점
├── providers/
│   └── cart_provider.dart # 장바구니 상태 관리
├── screens/
│   ├── login_screen.dart  # 로그인 화면
│   ├── pos_screen_v3.dart # POS 메인 화면
│   └── reservation_screen.dart # 예약 목록
├── services/
│   └── api_service.dart   # 백엔드 API 통신
└── widgets/
    ├── membership_dialog.dart # 멤버십 다이얼로그
    ├── payment_modal.dart     # 결제 모달
    └── receipt_dialog.dart    # 영수증 다이얼로그
```

## 설치 및 실행

### 사전 요구사항
- Flutter SDK 3.x 이상
- Visual Studio 2022 (Windows Desktop 빌드 시)
- Chrome (Web 빌드 시)

### 의존성 설치
```bash
flutter pub get
```

### Windows 실행
```bash
flutter run -d windows
```

### Web 실행
```bash
flutter run -d chrome
```

## 백엔드 연동

POS 앱은 **TG-Commerce API**(Port 8001)와 통신합니다.

### API 엔드포인트
| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/auth/token` | POST | 로그인 (OAuth2) |
| `/products/menu/{store_id}` | GET | 메뉴 조회 |
| `/orders/place` | POST | 주문 생성 |
| `/booking/list/{store_id}` | GET | 예약 목록 |
| `/membership/earn` | POST | 포인트 적립 |

### 기본 계정
- **ID**: `owner`
- **PW**: `1234`

## 관련 시스템

- **KDS (Kitchen Display)**: http://localhost:8001/kds
- **Commerce API Docs**: http://localhost:8001/docs
- **Core API Docs**: http://localhost:8000/docs

## 개발 히스토리

- **Gemini(CODER-X)**: 초기 개발 및 구조 설계
- **Claude**: 버그 수정 및 Windows 빌드 대응 (2024-12)
