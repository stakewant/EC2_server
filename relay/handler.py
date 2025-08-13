import requests
from flask import request
from route_table import ROUTE_TABLE

def relay_handler(path):
    """
    클라이언트로부터 받은 요청을 목적지 서버로 중계하고 응답을 반환
    """
    target_url = ROUTE_TABLE.get(f"/{path}")
    if not target_url:
        return {"error": f"Unknown endpoint: /{path}"}, 404

    try:
        # 요청 데이터 추출
        data = request.get_json()
        headers = {"Content-Type": "application/json"}

        # 목적지로 POST 요청 전송
        response = requests.post(target_url, json=data, headers=headers)

        # 결과 반환
        return response.json(), response.status_code

    except Exception as e:
        return {"error": f"중계 실패: {str(e)}"}, 500