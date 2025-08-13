import pymysql
from db.config import DB_CONFIG

def get_connection():
    """
    DB 연결을 생성해 반환합니다.
    """
    return pymysql.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        charset=DB_CONFIG["charset"],
        cursorclass=pymysql.cursors.DictCursor  # 결과를 딕셔너리로 반환
    )