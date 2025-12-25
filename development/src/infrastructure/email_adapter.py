import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List

from src.core.config import settings
from src.core.logger import logger
from src.domain.schemas import MessageRequest, SendResult, ContentType
from src.application.interfaces import ISenderService

class EmailAdapter(ISenderService):
    """
    SMTP 프로토콜을 이용한 이메일 전송 구현체
    """

    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.default_sender = settings.DEFAULT_SENDER

    def _create_mime_message(self, request: MessageRequest, to_email: str) -> MIMEMultipart:
        """이메일 메시지 객체 생성"""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = request.subject
        msg["From"] = request.sender or self.default_sender
        msg["To"] = to_email

        # 본문 인코딩 설정 (UTF-8)
        charset = "utf-8"
        part = MIMEText(request.body, "html" if request.content_type == ContentType.HTML else "plain", charset)
        msg.attach(part)
        
        return msg

    async def send(self, message: MessageRequest) -> SendResult:
        logger.info(f"Attempting to send email via SMTP: {self.host}:{self.port} | Request ID: {message.request_id}")
        
        # 수신자 목록 추출
        recipient_emails = [r.email for r in message.recipients]
        
        if not recipient_emails:
            logger.warning(f"No recipients found for Request ID: {message.request_id}")
            return SendResult(success=False, request_id=message.request_id, error_code="NO_RECIPIENTS", message="Recipient list is empty")

        try:
            # SMTP 연결 설정 (동기 방식, 향후 aiosmtplib으로 비동기 전환 가능)
            # 여기서는 편의상 표준 smtplib 사용 (블로킹 주의)
            with smtplib.SMTP(self.host, self.port) as server:
                server.ehlo()
                # TLS 보안 시작
                if self.port == 587:
                    server.starttls()
                    server.ehlo()
                
                # 로그인
                if self.user and self.password:
                    server.login(self.user, self.password)

                # 개별 발송 (Bulk 발송 시 전략 변경 필요)
                for to_email in recipient_emails:
                    msg = self._create_mime_message(message, to_email)
                    server.sendmail(msg["From"], to_email, msg.as_string())
            
            logger.success(f"Email sent successfully. Request ID: {message.request_id}")
            return SendResult(success=True, request_id=message.request_id)

        except smtplib.SMTPAuthenticationError:
            error_msg = "SMTP Authentication failed. Check credentials."
            logger.error(error_msg)
            return SendResult(success=False, request_id=message.request_id, error_code="AUTH_ERROR", message=error_msg)
            
        except smtplib.SMTPException as e:
            error_msg = f"SMTP Error: {str(e)}"
            logger.error(error_msg)
            return SendResult(success=False, request_id=message.request_id, error_code="SMTP_ERROR", message=error_msg)

        except Exception as e:
            error_msg = f"Unexpected error during email sending: {str(e)}"
            logger.exception(error_msg)
            return SendResult(success=False, request_id=message.request_id, error_code="UNKNOWN_ERROR", message=error_msg)

    async def validate_connection(self) -> bool:
        try:
            with smtplib.SMTP(self.host, self.port, timeout=5) as server:
                server.ehlo()
                if self.port == 587:
                    server.starttls()
                if self.user and self.password:
                    server.login(self.user, self.password)
            return True
        except Exception as e:
            logger.error(f"Connection validation failed: {e}")
            return False