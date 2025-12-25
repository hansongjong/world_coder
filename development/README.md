# World Coder Project

## 1. 개요
본 프로젝트는 **TG_MASTER_DESIGN**의 설계 사양을 준수하여 개발된 고성능 소프트웨어 시스템입니다.
**CODER-X**의 주도 하에 Clean Architecture 원칙과 SOLID 패턴을 적용하여 구현되었습니다.

## 2. 구조 (Architecture)
- **src/core**: 전역 설정, 로깅, 예외 처리 등 핵심 유틸리티
- **src/domain**: 비즈니스 엔티티 및 로직 (외부 의존성 없음)
- **src/application**: 유스케이스 구현 및 서비스 레이어
- **src/infrastructure**: 데이터베이스, 외부 API 통신 등 기술적 구현
- **src/interface**: 사용자/시스템 인터페이스 (API, CLI 등)

## 3. 설치 및 실행 (Installation & Usage)

### 사전 요구사항
- Python 3.9 이상

### 설치
```bash
# 1. 가상환경 생성
python -m venv venv

# 2. 가상환경 활성화
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt
```

### 실행
```bash
python src/main.py
```

## 4. 개발 가이드
- 모든 커밋 전 `pytest`를 통한 단위 테스트 통과 필수.
- 코드 스타일은 `Black`과 `Flake8`을 준수.