import os
import hashlib
import hmac
import base64

def verify_kakao_signature(request):
    try:
        timestamp = request.headers['X-Kakao-Signature']
        signature = base64.b64encode(hmac.new(os.environ['KAKAO_API_KEY'].encode('utf-8'), timestamp.encode('utf-8'), hashlib.sha256).digest()).decode('utf-8')
        return signature == request.headers.get('X-Kakao-Signature')
    except Exception as e:
        print(f"카카오 서명 검증 중 오류 발생: {str(e)}")
        return False