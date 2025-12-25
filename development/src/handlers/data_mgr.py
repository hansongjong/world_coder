import json
import os
from typing import Dict, Any
from sqlalchemy.orm import Session
from src.database.engine import SessionLocal
from src.core.serverless.handler import BaseFunction
from src.core.config import settings
from src.core.database.v3_extensions import TargetList

class DataImportFunction(BaseFunction):
    """
    Code: FN_DATA_IMPORT
    Description: 타겟 리스트(CSV/TXT) 파싱 및 DB 등록
    """
    
    def handle(self, event: Dict[str, Any]) -> Dict[str, Any]:
        list_name = event.get("name")
        raw_data = event.get("raw_data") # Base64 encoded or raw text
        source_type = event.get("source_type", "UPLOAD")
        
        self.audit("DATA_IMPORT", f"Importing list: {list_name}")
        
        # 데이터 파싱 (단순 줄바꿈 기준)
        lines = [line.strip() for line in raw_data.split('\n') if line.strip()]
        total_count = len(lines)
        
        # 파일로 저장 (DB 부하 방지)
        file_id = f"list_{self.context.req_id}"
        file_path = settings.BASE_DIR / "data" / f"{file_id}.txt"
        
        os.makedirs(file_path.parent, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
            
        # DB 등록
        db: Session = SessionLocal()
        try:
            new_list = TargetList(
                list_id=file_id,
                user_id=self.context.user_id,
                name=list_name,
                source_type=source_type,
                total_count=total_count,
                valid_count=total_count, # 추후 검증 로직 추가 가능
                file_path=str(file_path),
                preview_data=lines[:5] # 미리보기 5개
            )
            db.add(new_list)
            db.commit()
            
            return {
                "status": "success",
                "list_id": file_id,
                "count": total_count,
                "preview": lines[:5]
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            db.close()