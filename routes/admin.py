from flask import Blueprint, request, jsonify
from db.mysql_connector import get_connection

admin_route = Blueprint("admin", __name__)

@admin_route.route("/admin/query", methods=["POST"])
def run_custom_query():
    data = request.get_json()
    query = data.get("query")

    if not query:
        return jsonify({"error": "query 파라미터가 필요합니다."}), 400

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(query)
            if query.strip().lower().startswith("select"):
                result = cursor.fetchall()
                return jsonify({"result": result}), 200
            else:
                conn.commit()
                return jsonify({"message": "쿼리 실행 완료", "affected": cursor.rowcount}), 200
    except Exception as e:
        return jsonify({"error": f"쿼리 실행 오류: {str(e)}"}), 500
    finally:
        conn.close()