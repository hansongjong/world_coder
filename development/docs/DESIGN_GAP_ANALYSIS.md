# TG-SYSTEM Design Gap Analysis Report

**Date**: 2024-05-23
**Reviewer**: CODER-X (Senior Software Engineer)
**Status**: Critical Gaps Identified for Production Launch

## 1. 충분한 영역 (Sufficient Design)
다음 영역은 제공된 설계 도서(`TG_Master_Design/*`)를 통해 개발이 가능한 수준입니다.
*   **데이터베이스 모델링**: `TG_Master_Schema_Viewer`를 통해 V3 스키마(Core, Commerce)가 명확히 정의됨.
*   **백엔드 로직**: `TG_Serverless_Architecture` 및 로드맵을 통해 Kernel, ERP, Scheduler 구조 확립됨.
*   **API 명세**: 서비스 카탈로그를 통해 입/출력 파라미터 유추 가능.

## 2. 부족하거나 누락된 영역 (Missing / Insufficient)

### 2.1 프론트엔드 UI/UX 상세 설계 (Frontend Design)
현재 `TG_System_Dashboard_KR.html`은 개념적인 와이어프레임 수준입니다.
*   **POS 앱 디자인**: Flutter 앱의 화면별(로그인, 테이블 배치, 결제, 영수증) 디자인 시안(Figma/Zeplin) 부재.
*   **웹 대시보드**: 관리자 페이지의 구체적인 UI 컴포넌트(차트 라이브러리, 테이블 스타일, 테마) 정의 부재.
*   **결과**: 개발자가 임의로 UI를 구성해야 하므로, UX 품질이 일관되지 않을 수 있음.

### 2.2 결제 및 외부 인터페이스 규격 (External Interfaces)
설계도상에는 "PG 결제"라고만 명시되어 있습니다.
*   **PG사 연동 규격**: 포트원(Iamport), 토스페이먼트 등 구체적인 PG사 선정 및 API 키, Webhook 보안 설정 누락.
*   **IoT 프로토콜**: "문열림" 기능은 있으나, 실제 하드웨어(MQTT, Modbus, RS485)와의 통신 프로토콜 명세 부재. 현재는 Mock(가상)으로만 구현됨.

### 2.3 인프라 및 배포 (DevOps)
로컬 Docker 실행은 가능하나, 상용 운영을 위한 설계가 부족합니다.
*   **CI/CD 파이프라인**: GitHub Actions 또는 Jenkins를 통한 자동 배포 스크립트.
*   **클라우드 리소스**: AWS/GCP 사용 시 로드밸런서(ALB), 오토스케일링 그룹(ASG), RDS 설정 값.
*   **비밀 관리**: `.env` 파일 외에 AWS Secrets Manager나 HashiCorp Vault 같은 프로덕션급 비밀 관리 전략.

## 3. 제안 및 액션 플랜 (Action Plan)

### Step 1. 프론트엔드 표준 정의 (Design System)
*   **POS**: Material Design 3.0 기반의 표준 위젯 카탈로그 작성 필요.
*   **Web**: AdminLTE 또는 MUI 같은 오픈소스 템플릿 도입 결정 필요.

### Step 2. 외부 연동 명세화 (Interface Spec)
*   **PG**: 테스트 결제를 위한 'PortOne' 연동 코드 작성.
*   **IoT**: MQTT 브로커(Mosquitto) 도입 및 토픽(Topic) 구조 설계.

### Step 3. 테스트 시나리오 (QA)
*   단순 기능 구현을 넘어, 동시 접속자 100명 상황에서의 부하 테스트(Locust) 시나리오 작성 필요.

---

**결론 (Verdict)**: 
개발자(CODER-X)가 "기능"을 만들 수는 있으나, "제품"으로 출시하기 위해서는 **UI 디자인 시안**과 **실제 하드웨어/PG 연동 정보**가 추가로 제공되어야 합니다.