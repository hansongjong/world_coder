# TG-SYSTEM Design Traceability Matrix

본 문서는 `TG_MASTER_DESIGN`의 설계 요구사항이 실제 코드(`src/`)로 어떻게 구현되었는지 증명합니다.

## 1. 데이터베이스 및 스키마 (Database)
| 설계 문서 (Design Source) | 요구사항 (Requirement) | 구현 코드 (Implementation) | 상태 |
|:---|:---|:---|:---:|
| **TG_Master_Schema_Viewer.html** | User, Subscription 테이블 | `src/core/database/v3_schema.py` (Class MasterUser) | ✅ |
| **TG_Master_Schema_Viewer.html** | Audit Log (법적 증빙) | `src/core/database/v3_schema.py` (Class AuditLog) | ✅ |
| **TG_Service_Deployment_Mapper.html** | Service Catalog (상품) | `src/core/database/v3_schema.py` (Class FunctionCatalog) | ✅ |
| **TG_Dev_Roadmap.html (Phase 2)** | Session, Target Data | `src/core/database/v3_extensions.py` | ✅ |
| **TG_Dev_Roadmap.html (Phase 3)** | Campaign, Schedule | `src/core/database/v3_campaigns.py` | ✅ |

## 2. 아키텍처 및 코어 (Architecture)
| 설계 문서 (Design Source) | 요구사항 (Requirement) | 구현 코드 (Implementation) | 상태 |
|:---|:---|:---|:---:|
| **TG_Serverless_Architecture.html** | Function 단위 실행 격리 | `src/core/kernel.py` (SystemKernel) | ✅ |
| **TG_ERP_Architecture.html** | 과금 확인 로직 (Pre-check) | `src/core/erp_service.py` | ✅ |
| **TG_Legal_Process.html** | 모든 행위의 불변 로그 기록 | `src/core/kernel.py` (LegalAuditService integration) | ✅ |

## 3. 기능 구현 (Functionality)
| 설계 문서 (Design Source) | 요구사항 (Requirement) | 구현 코드 (Implementation) | 상태 |
|:---|:---|:---|:---:|
| **TG_Service_Deployment_Catalog.html** | TG Message Sender | `src/handlers/tg_sender.py` | ✅ |
| **TG_Service_Deployment_Catalog.html** | Group Scraper | `src/handlers/tg_scraper.py` | ✅ |
| **TG_Dev_Roadmap.html (Phase 3)** | Campaign Dispatcher | `src/handlers/campaign_mgr.py` | ✅ |
| **TG_Dev_Roadmap.html (Phase 3)** | Scheduler (Cron) | `src/core/scheduler.py` | ✅ |

## 4. 미구현 및 향후 과제 (Missing / TODO)
| 설계 문서 (Design Source) | 누락 기능 (Missing Feature) | 계획 (Plan) |
|:---|:---|:---|
| **TG_System_Dashboard_KR.html** | **대시보드 통계 데이터 API** | **금일 구현 예정** |
| **TG_Serverless_Architecture.html** | Docker Container 격리 실행 | 로컬 프로세스 실행으로 대체됨 (Phase 4 예정) |
| **TG_Legal_Process.html** | PDF 증빙서 자동 생성 | 데이터는 쌓이고 있으나 PDF 변환기 미구현 |