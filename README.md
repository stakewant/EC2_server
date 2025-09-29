# EC2_server

Python Flask 기반 서버  

사용자 관리, 퀴즈, 즐겨찾기, 공지사항, 논문 검색 등의 기능을 API 형태로 제공    
AWS EC2에 직접 배포하여 운영할 수 있으며, 데이터베이스는 MySQL 사용

---

##  기술 스택
- Python 3.10
- Flask
- MySQL
- PyMySQL
- AWS EC2 (Ubuntu 20.04)

---
## 프로젝트 구조
~~~shell
EC2_server/
├── main.py                    # Flask 실행 진입점
├── requirements.txt           # Python 패키지 목록
├── route_table.py             # 라우트 테이블 (동적 매핑):서버 내부에 처리불가한 모듈을 서버외부에서 처리하고 그 모듈로 중계
├── .env                       # 환경변수 파일: 이메일 전송 정보
├── .gitattributes             # Git 속성 설정
│
├── relay/                     # 요청 중계/핸들러
│   └── handler.py
│
├── routes/                    # API 라우팅 모듈 (Flask Blueprint): 서버 내부 처리 가능한 기능 수행
│   ├── admin.py               # DB관리자 API
│   ├── notice.py              # 공지사항 API
│   ├── user.py                # 사용자 계정 관리 API
│   ├── favorite.py            # 즐겨찾기 API
│   ├── progress.py            # 진행도/학습현황 API
│   ├── quiz.py                # 퀴즈 API
│   ├── model.py               # 3D 모델 검색 API
│   ├── paper.py               # 논문 검색/번역 API
│   └── search.py              # 분자 모델 검색 API
│
├── db/                        # 데이터베이스 관련 DAO & 설정
│   ├── config.py              # DB 설정값 (config)
│   ├── mysql_connector.py     # MySQL 연결 모듈
│   ├── auth/                  # 인증 관련 DAO: 이메일 인증
│   │   └── dao.py
│   ├── favorite/              # 즐겨찾기 DAO: 사용자가 앱에서 설정한 퀴즈 즐겨찾기 정보
│   │   └── dao.py
│   ├── notice/                # 공지사항 DAO: 관리자가 직접 입력한 공지사항
│   │   └── dao.py
│   ├── progress/              # 퀴즈 진행도/학습현황 DAO: 앱 종료 시점에 사용자의 퀴즈 진행도
│   │   └── dao.py
│   ├── quiz/                  # 퀴즈 DAO: 퀴즈 호출
│   │   └── dao.py
│   └── user/                  # 사용자 DAO: 회원가입/회원탈퇴/로그인 등의 회원 계정 관련 
│       └── dao.py
│
└── utils/                     # 공용 유틸리티
    ├── email.py               # 이메일 전송 기능
    └── security.py            # 보안/비밀번호 해시 관련
~~~
---


# API 엔드포인트

##  EC2_server/routes/ 안에 정의된 API
| 모듈(routes)      | Method | Endpoint              | 설명                  |
| --------------- | ------ | --------------------- | ------------------- |
| **user.py**     | POST   | `/users/register`     | 사용자 회원가입            |
|                 | POST   | `/users/delete`       | 사용자 탈퇴              |
|                 | POST   | `/users/send-code`    | 이메일 인증 코드 발송        |
|                 | POST   | `/users/verify-code`  | 이메일 인증 코드 검증        |
|                 | GET    | `/users/info`         | 사용자 정보 조회           |
|                 | POST   | `/users/update-pw`    | 비밀번호 변경 (이메일 기반)    |
|                 | POST   | `/users/login`        | 로그인 (ID/비밀번호 검증)    |
| **quiz.py**     | POST   | `/quizzes/upload`     | 퀴즈 파일 업로드(JSON/CSV) |
|                 | GET    | `/quizzes/<id>`       | 특정 퀴즈 조회            |
|                 | GET    | `/quizzes/amino/<aa>` | 아미노산별 퀴즈 목록 조회      |
| **progress.py** | POST   | `/progress/update`    | 사용자 학습 진행도 갱신       |
|                 | GET    | `/progress`           | 전체 학습 진행도 조회        |
| **notice.py**   | GET    | `/notice`             | 공지사항 목록 조회          |
|                 | POST   | `/notice/create`      | 공지사항 등록 (관리자)       |
| **favorite.py** | POST   | `/favorite/add`       | 즐겨찾기 추가             |
|                 | POST   | `/favorite/remove`    | 즐겨찾기 삭제             |
|                 | GET    | `/favorite/list`      | 즐겨찾기 목록 조회          |
| **paper.py**    | GET    | `/papers`             | 논문 검색 및 번역          |
| **model.py**    | POST   | `/model/compose`      | 3D 모델 조합            |
| **search.py**   | POST   | `/search`             | 데이터 검색 API          |
| **admin.py**    | GET    | `/admin/users`        | 전체 사용자 목록 조회 (관리자)  |
|                 | POST   | `/admin/delete-user`  | 특정 사용자 강제 삭제        |

# 📑 API 오류 코드 상세표

##  User API

| 엔드포인트 | 상황 | HTTP | code | 메시지 예시 |
|------------|------|------|------|-------------|
| **POST /users/register** | 필수 필드 누락 | 400 | BAD_REQUEST | "모든 필드를 입력해주세요." |
| | 이메일 중복 | 409 | CONFLICT | "이미 존재하는 이메일입니다." |
| | DB 오류 | 500 | INTERNAL_SERVER_ERROR | "DB 오류: ..." |
| **POST /users/delete** | user_id 누락 | 400 | BAD_REQUEST | "user_id는 필수입니다." |
| | 존재하지 않는 유저 | 404 | NOT_FOUND | "존재하지 않는 사용자입니다." |
| **GET /users/info** | user_id 누락 | 400 | BAD_REQUEST | "user_id가 필요합니다." |
| | 유저 없음 | 404 | NOT_FOUND | "사용자를 찾을 수 없습니다." |
| **POST /users/send-code** | email 누락 | 400 | BAD_REQUEST | "email이 필요합니다." |
| | DB 오류 | 500 | INTERNAL_SERVER_ERROR | "DB 오류: ..." |
| | 메일 발송 실패 | 500 | INTERNAL_SERVER_ERROR | "이메일 발송 실패: ..." |
| **POST /users/verify-code** | email/code 누락 | 400 | BAD_REQUEST | "email, code 모두 필요" |
| | 코드 없음 | 404 | NOT_FOUND | "코드가 존재하지 않음" |
| | 코드 만료 | 400 | BAD_REQUEST | "코드 만료" |
| | 코드 불일치 | 400 | BAD_REQUEST | "코드 불일치" |
| **POST /users/reset-password** | email/new_password 누락 | 400 | BAD_REQUEST | "email, new_password 모두 필요" |
| | 비밀번호 너무 짧음 | 400 | BAD_REQUEST | "비밀번호는 8자 이상이어야 합니다." |
| | 존재하지 않는 이메일 | 404 | NOT_FOUND | "존재하지 않는 이메일입니다." |
| | DB 오류 | 500 | INTERNAL_SERVER_ERROR | "DB 오류: ..." |
| **POST /users/login** | 파라미터 누락 | 400 | BAD_REQUEST | "identifier, password 모두 필요" |
| | 아이디/비밀번호 틀림 | 401 | UNAUTHORIZED | "아이디/이메일 또는 비밀번호가 올바르지 않습니다." |

---

##  Quiz API

| 엔드포인트 | 상황 | HTTP | code | 메시지 예시 |
|------------|------|------|------|-------------|
| **POST /quizzes/upload** | 파일 없음 | 400 | BAD_REQUEST | "파일이 포함되지 않았습니다." |
| | 지원되지 않는 확장자 | 400 | BAD_REQUEST | "지원되지 않는 파일 형식입니다." |
| | DB 오류 | 500 | INTERNAL_SERVER_ERROR | "DB 오류: ..." |
| **GET /quizzes/<quiz_id>** | 퀴즈 없음 | 404 | NOT_FOUND | "퀴즈를 찾을 수 없습니다." |
| | DB 오류 | 500 | INTERNAL_SERVER_ERROR | "DB 오류: ..." |
| **GET /quizzes?amino_acid=** | 파라미터 누락 | 400 | BAD_REQUEST | "amino_acid 파라미터가 필요합니다." |
| **POST /quiz/log** | user_id/status 누락 | 400 | BAD_REQUEST | "user_id, status(correct\|wrong) 필요" |
| | DB 오류 | 500 | INTERNAL_SERVER_ERROR | "진행도 갱신 실패: ..." |
| **GET /quiz/logs/<user_id>** | DB 오류 | 500 | INTERNAL_SERVER_ERROR | "조회 실패: ..." |

---

##  Progress API

| 엔드포인트 | 상황 | HTTP | code | 메시지 예시 |
|------------|------|------|------|-------------|
| **GET /progress/overall** | user_id 누락 | 400 | BAD_REQUEST | "user_id 필요" |
| | DB 오류 | 500 | INTERNAL_SERVER_ERROR | "DB 오류: ..." |
| **POST /progress/overall/set** | 필드 누락 | 400 | BAD_REQUEST | "user_id, total_solved, total_questions 필요" |
| | DB 오류 | 500 | INTERNAL_SERVER_ERROR | "DB 오류: ..." |

---

##  Notice API

| 엔드포인트 | 상황 | HTTP | code | 메시지 예시 |
|------------|------|------|------|-------------|
| **GET /notices** | DB 오류 | 500 | INTERNAL_SERVER_ERROR | "DB 오류: ..." |

---

##  Favorite API

| 엔드포인트 | 상황 | HTTP | code | 메시지 예시 |
|------------|------|------|------|-------------|
| **POST /favorites/add** | 필수값 누락 | 400 | BAD_REQUEST | "user_id, chapter_id 필요" |
| | DB 오류 | 500 | INTERNAL_SERVER_ERROR | "DB 오류: ..." |
| **POST /favorites/remove** | 필수값 누락 | 400 | BAD_REQUEST | "user_id, chapter_id 필요" |
| | DB 오류 | 500 | INTERNAL_SERVER_ERROR | "DB 오류: ..." |
| **GET /favorites** | user_id 누락 | 400 | BAD_REQUEST | "user_id 필요" |
| | DB 오류 | 500 | INTERNAL_SERVER_ERROR | "DB 오류: ..." |

---

##  Paper API

| 엔드포인트 | 상황 | HTTP | code | 메시지 예시 |
|------------|------|------|------|-------------|
| **GET /papers?query=** | query 누락 | 400 | BAD_REQUEST | "Query parameter required" |
| | PubMed API 오류 | 500 | INTERNAL_SERVER_ERROR | "PubMed 검색 오류: ..." |
| | 번역 오류 | 500 | INTERNAL_SERVER_ERROR | "(번역 실패)" |

---

##  Model API

| 엔드포인트 | 상황 | HTTP | code | 메시지 예시 |
|------------|------|------|------|-------------|
| **POST /model/compose** | 잘못된 입력(JSON 오류 등) | 400 | BAD_REQUEST | "요청 데이터가 잘못되었습니다." |
| | 처리 중 오류 | 500 | INTERNAL_SERVER_ERROR | "처리 중 오류 발생: ..." |

---

##  Search API

| 엔드포인트 | 상황 | HTTP | code | 메시지 예시 |
|------------|------|------|------|-------------|
| **GET /from_name?name=** | name 누락 | 400 | BAD_REQUEST | "name parameter required" |
| | 화합물 없음 | 404 | NOT_FOUND | "Compound not found" |
| | 처리 중 오류 | 500 | INTERNAL_SERVER_ERROR | "에러 메시지" |

---

##  공통 전역 에러

| 상황 | HTTP | code | 메시지 |
|------|------|------|--------|
| 잘못된 요청 | 400 | BAD_REQUEST | "잘못된 요청입니다." |
| 존재하지 않는 경로 | 404 | NOT_FOUND | "리소스를 찾을 수 없습니다." |
| 지원하지 않는 메서드 | 405 | METHOD_NOT_ALLOWED | "허용되지 않은 메서드입니다." |
| 업로드 용량 초과 | 413 | PAYLOAD_TOO_LARGE | "업로드 용량 제한을 초과했습니다." |
| 서버 내부 오류 | 500 | INTERNAL_SERVER_ERROR | "서버 내부 오류" |
