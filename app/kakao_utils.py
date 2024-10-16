import os
import hashlib
import hmac
import base64
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_kakao_signature(request):
    try:
        timestamp = request.headers['X-Kakao-Timestamp']
        signature = request.headers['X-Kakao-Signature']
        computed_signature = base64.b64encode(
            hmac.new(
                os.environ['KAKAO_API_KEY'].encode('utf-8'),
                timestamp.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        return signature == computed_signature
    except Exception as e:
        logger.error(f"카카오 서명 검증 중 오류 발생: {str(e)}")
        return False
