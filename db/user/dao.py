from db.mysql_connector import get_connection
import uuid  # 상단에 추가

# 내부에서 salt 생성
salt = str(uuid.uuid4())


def insert_user(data):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (data["email"],))
            if cursor.fetchone():
                return {"error": "이미 존재하는 이메일입니다."}, 409

            cursor.execute("""
                           INSERT INTO users (user_id, username, password, salt, email, birth_date)
                           VALUES (%s, %s, %s, %s, %s, %s)
                           """, (
                               data["user_id"],
                               data["username"],
                               data["password"],
                               salt,
                               data["email"],
                               data["birth_date"]
                           ))
            conn.commit()
            return {"message": "회원가입 성공!"}, 201

    except Exception as e:
        return {"error": f"DB 오류: {str(e)}"}, 500

def delete_user(data):
            conn = get_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM users WHERE user_id = %s", (data["user_id"],))
                    if cursor.fetchone() is None:
                        return {"error": "존재하지 않는 사용자입니다."}, 404

                    cursor.execute("DELETE FROM users WHERE user_id = %s", (data["user_id"],))
                    conn.commit()
                    return {"message": "회원 삭제 성공!"}, 200

            except Exception as e:
                return {"error": f"DB 오류: {str(e)}"}, 500

def get_user_info(user_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT user_id, username, email, birth_date
                FROM users
                WHERE user_id = %s
            """, (user_id,))
            user = cursor.fetchone()

            if user is None:
                return {"error": "사용자를 찾을 수 없습니다."}, 404

            return {"user": user}, 200

    except Exception as e:
        return {"error": f"DB 오류: {str(e)}"}, 500