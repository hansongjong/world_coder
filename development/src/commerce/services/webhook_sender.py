"""
WebhookSender - TgMain 연동 Webhook 발송 서비스
"""
import os
import json
import uuid
import hmac
import hashlib
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)


class WebhookSender:
    """TgMain Webhook 발송 클래스"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("TGMAIN_API_KEY", "")
        self.secret_key = secret_key or os.getenv("TGMAIN_SECRET_KEY", "")
        self.base_url = base_url or os.getenv("TGMAIN_BASE_URL", "https://api.tgmain.io")
        self.webhook_path = "/api/v1/webhooks/receive"
        self.timeout = 5.0
        self.max_retries = 5

    def _generate_signature(self, method: str, path: str, timestamp: str, body: str) -> str:
        """HMAC-SHA256 서명 생성"""
        body_hash = hashlib.sha256(body.encode()).hexdigest()
        message = f"{method}\n{path}\n{timestamp}\n{body_hash}"
        return hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

    def _build_webhook_payload(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Webhook 페이로드 구성"""
        return {
            "webhook_id": f"wh_{uuid.uuid4().hex[:12]}",
            "event_type": event_type,
            "event_version": "1.0",
            "source": "world_pos",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "delivery_attempt": 1,
            "payload": payload
        }

    async def send_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        store_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Webhook 이벤트 발송

        Args:
            event_type: 이벤트 유형 (ORDER_PAID, STOCK_LOW 등)
            payload: 이벤트 데이터
            store_id: 매장 ID (선택)

        Returns:
            dict: 발송 결과 {"success": bool, "response": ..., "error": ...}
        """
        if not self.api_key or not self.secret_key:
            logger.warning("TgMain API credentials not configured, skipping webhook")
            return {"success": False, "error": "API credentials not configured"}

        timestamp = datetime.utcnow().isoformat() + "Z"
        webhook_data = self._build_webhook_payload(event_type, payload)

        if store_id:
            webhook_data["store_id"] = store_id

        body = json.dumps(webhook_data, ensure_ascii=False)
        signature = self._generate_signature("POST", self.webhook_path, timestamp, body)

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
            "X-Timestamp": timestamp,
            "X-Signature": signature
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}{self.webhook_path}",
                    content=body,
                    headers=headers,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    logger.info(f"Webhook sent: {event_type}")
                    return {
                        "success": True,
                        "response": response.json() if response.text else {},
                        "status_code": response.status_code
                    }
                else:
                    logger.error(f"Webhook failed: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": response.text,
                        "status_code": response.status_code
                    }

        except httpx.TimeoutException:
            logger.error(f"Webhook timeout: {event_type}")
            return {"success": False, "error": "Request timeout"}
        except httpx.RequestError as e:
            logger.error(f"Webhook error: {event_type} - {str(e)}")
            return {"success": False, "error": str(e)}

    async def send_order_paid(
        self,
        order_id: str,
        store_id: int,
        total_amount: int,
        payment_method: str,
        items: list
    ) -> Dict[str, Any]:
        """주문 결제 완료 이벤트 발송"""
        payload = {
            "order_id": order_id,
            "store_id": store_id,
            "total_amount": total_amount,
            "payment_method": payment_method,
            "items": items,
            "paid_at": datetime.utcnow().isoformat() + "Z"
        }
        return await self.send_event("ORDER_PAID", payload, store_id)

    async def send_order_refunded(
        self,
        order_id: str,
        store_id: int,
        refund_amount: int,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """환불 완료 이벤트 발송"""
        payload = {
            "order_id": order_id,
            "store_id": store_id,
            "refund_amount": refund_amount,
            "reason": reason,
            "refunded_at": datetime.utcnow().isoformat() + "Z"
        }
        return await self.send_event("ORDER_REFUNDED", payload, store_id)

    async def send_stock_low(
        self,
        store_id: int,
        item_code: str,
        item_name: str,
        current_qty: int,
        min_qty: int
    ) -> Dict[str, Any]:
        """재고 부족 이벤트 발송"""
        payload = {
            "store_id": store_id,
            "item_code": item_code,
            "item_name": item_name,
            "current_quantity": current_qty,
            "minimum_quantity": min_qty,
            "shortage": min_qty - current_qty,
            "detected_at": datetime.utcnow().isoformat() + "Z"
        }
        return await self.send_event("STOCK_LOW", payload, store_id)

    async def send_delivery_received(
        self,
        store_id: int,
        po_number: str,
        vendor_name: str,
        items: list,
        received_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """입고 확인 이벤트 발송"""
        payload = {
            "store_id": store_id,
            "po_number": po_number,
            "vendor_name": vendor_name,
            "items": items,
            "received_by": received_by,
            "received_at": datetime.utcnow().isoformat() + "Z"
        }
        return await self.send_event("DELIVERY_RECEIVED", payload, store_id)

    async def send_member_created(
        self,
        store_id: int,
        member_id: int,
        phone: str,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """회원 가입 이벤트 발송"""
        payload = {
            "store_id": store_id,
            "member_id": member_id,
            "phone": phone,
            "name": name,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        return await self.send_event("MEMBER_CREATED", payload, store_id)


# 싱글톤 인스턴스
webhook_sender = WebhookSender()
