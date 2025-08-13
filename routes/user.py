from flask import Blueprint, request, jsonify
from db.user.dao import insert_user, delete_user, get_user_info

user_route = Blueprint("user", __name__)

@user_route.route("/users/register", methods=["POST"])
def register_user():
    data = request.get_json()
    required_fields = ["user_id", "username", "password", "email", "birth_date"]

    if not all(field in data and data[field] for field in required_fields):
        return jsonify({"error": "모든 필드를 입력해주세요."}), 400

    result, status = insert_user(data)
    return jsonify(result), status


@user_route.route("/users/delete", methods=["POST"])
def delete_user_route():
    data = request.get_json()
    if not data.get("user_id"):
        return jsonify({"error": "user_id는 필수입니다."}), 400

    result, status = delete_user(data)
    return jsonify(result), status


@user_route.route("/users/info", methods=["GET"])
def get_user_info_route():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id가 필요합니다."}), 400

    result, status = get_user_info(user_id)
    return jsonify(result), status