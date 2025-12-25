# TG-SYSTEM Enterprise Quick Start Demo

"아무것도 구현되지 않았다"는 오해를 풀기 위해 준비된 **즉시 실행 패키지**입니다.
이 패키지는 DB 구축부터 캠페인 실행까지 **단 한 번의 명령**으로 시연합니다.

## 1. 준비
```bash
pip install -r requirements_demo.txt
```

## 2. 자동 시연 실행 (Auto Demo)
이 스크립트는 초기화, 데이터 생성, 캠페인 스케줄링, 작업 분배를 자동으로 수행합니다.
```bash
python run_full_demo.py
```
*성공 시 "Dispatcher created N sub-tasks" 메시지가 출력됩니다.*

## 3. 실시간 대시보드 (Live Monitor)
시스템 내부에서 일어나는 일(작업 큐, 로그, 상태)을 실시간 그래픽으로 확인합니다.
```bash
python src/interface/cli_dashboard.py
```

## 4. 포함된 핵심 모듈
1. **Core Kernel**: `src/core/kernel.py` (ERP/Audit 내장)
2. **Master DB**: `src/core/database/` (V3 스키마 전체)
3. **Handlers**: `src/handlers/` (실제 동작하는 서버리스 함수들)
4. **Scheduler**: `src/core/scheduler.py` (캠페인 자동 감지기)