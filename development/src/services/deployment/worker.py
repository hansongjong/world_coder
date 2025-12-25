import asyncio
import traceback
from sqlalchemy.orm import Session
from src.database.engine import SessionLocal
from src.database.models import Deployment, ServiceCatalog
from src.services.factory import ServiceFactory
from src.core.logger import logger

async def process_deployment(deployment_id: str):
    """개별 배포 작업 처리"""
    db: Session = SessionLocal()
    try:
        # 1. 배포 정보 로드
        deployment = db.get(Deployment, deployment_id)
        if not deployment:
            return

        # 상태 변경: running
        deployment.status = "running"
        db.commit()

        # 2. 서비스 클래스 로드
        service_code = deployment.service.service_code
        ServiceClass = ServiceFactory.get_service_class(service_code)
        
        # 3. 서비스 인스턴스화 및 실행
        service_instance = ServiceClass(
            deployment_id=deployment.id,
            config=deployment.instance_config,
            db=db
        )
        
        logger.info(f"[Worker] Starting Deployment {deployment_id} ({service_code})")
        await service_instance.execute()
        
        # 4. 성공 처리
        deployment.status = "completed"
        db.commit()
        logger.success(f"[Worker] Deployment {deployment_id} Completed.")

    except Exception as e:
        logger.error(f"[Worker] Deployment {deployment_id} Failed: {e}")
        traceback.print_exc()
        
        # 실패 처리
        deployment.status = "failed"
        db.commit()
    finally:
        db.close()

async def worker_loop():
    """메인 워커 루프"""
    logger.info("[Worker] Service Execution Worker Started.")
    
    while True:
        db: Session = SessionLocal()
        try:
            # Pending 상태의 작업 조회 (한 번에 하나씩 처리)
            # 동시성을 높이려면 여기서 여러 개를 가져와 asyncio.gather 사용
            deployment = db.query(Deployment).filter(Deployment.status == "pending").first()
            
            if deployment:
                # 즉시 처리 (비동기 Task로 넘김)
                asyncio.create_task(process_deployment(deployment.id))
            
        except Exception as e:
            logger.error(f"[Worker] Loop Error: {e}")
        finally:
            db.close()
            
        # 1초 대기 (폴링 간격)
        await asyncio.sleep(1)

if __name__ == "__main__":
    # 워커 단독 실행 모드
    asyncio.run(worker_loop())