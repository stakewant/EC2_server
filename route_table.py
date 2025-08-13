# route_table.py

# 클라이언트가 보낸 요청의 엔드포인트와 목적지 서버의 URL을 매핑
ROUTE_TABLE = {
    "/model/compose": "http://127.0.0.1:5001/model/compose",      # POST
    "/papers": "http://127.0.0.1:5002/paper/search",        # 논문 검색 및 번역
    "/chat/generate": "http://127.0.0.1:5003/chat/generate",      # 챗봇 채팅
    "/auth/login": "http://127.0.0.1:5004/auth/login",            # 로그인
    "/notice/list": "http://127.0.0.1:5005/notice/list",          # 공지사항
    "/email/send-code": "http://127.0.0.1:5006/email/send-code"   # 이메일 인증
    "/quizzes/"                                            # GET
    "/search/from_name"                           #GET

}