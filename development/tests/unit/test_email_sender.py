import pytest
from unittest.mock import MagicMock, patch
from src.infrastructure.email_adapter import EmailAdapter
from src.domain.schemas import MessageRequest, Recipient, ChannelType

@pytest.fixture
def email_adapter():
    return EmailAdapter()

@pytest.fixture
def valid_message():
    return MessageRequest(
        request_id="test-001",
        channel=ChannelType.EMAIL,
        recipients=[Recipient(email="test@example.com")],
        subject="Test Subject",
        body="Test Body"
    )

@pytest.mark.asyncio
async def test_send_email_success(email_adapter, valid_message):
    """SMTP 연결 및 전송 성공 시나리오 테스트"""
    
    # smtplib.SMTP 객체를 모킹
    with patch("smtplib.SMTP") as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # 실행
        result = await email_adapter.send(valid_message)
        
        # 검증
        assert result.success is True
        assert result.request_id == "test-001"
        mock_server.sendmail.assert_called_once()  # sendmail이 호출되었는지 확인

@pytest.mark.asyncio
async def test_send_email_auth_failure(email_adapter, valid_message):
    """SMTP 인증 실패 시나리오 테스트"""
    
    import smtplib
    
    with patch("smtplib.SMTP") as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # 로그인 시 인증 에러 발생하도록 설정
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, "Auth Failed")
        
        # 실행
        result = await email_adapter.send(valid_message)
        
        # 검증
        assert result.success is False
        assert result.error_code == "AUTH_ERROR"

@pytest.mark.asyncio
async def test_validate_connection_success(email_adapter):
    """연결 확인 기능 테스트"""
    with patch("smtplib.SMTP") as mock_smtp:
        mock_smtp.return_value.__enter__.return_value = MagicMock()
        assert await email_adapter.validate_connection() is True

@pytest.mark.asyncio
async def test_validate_connection_failure(email_adapter):
    """연결 실패 확인 기능 테스트"""
    with patch("smtplib.SMTP") as mock_smtp:
        # SMTP 연결 자체가 에러를 뱉음
        mock_smtp.side_effect = Exception("Connection Timeout")
        assert await email_adapter.validate_connection() is False