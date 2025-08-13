from flask import Blueprint, request, jsonify
import json
import pandas as pd
from db.quiz.dao import insert_many_quizzes,get_quiz_by_id, get_quizzes_by_amino_acid

quiz_bp = Blueprint("quiz", __name__)

@quiz_bp.route("/quizzes/upload", methods=["POST"])
def upload_quiz_file():
    if 'file' not in request.files:
        return jsonify({"error": "파일이 포함되지 않았습니다."}), 400

    file = request.files['file']

    try:
        if file.filename.endswith('.json'):
            quiz_list = json.load(file)
        elif file.filename.endswith('.csv'):
            df = pd.read_csv(file)
            quiz_list = df.to_dict(orient="records")
        else:
            return jsonify({"error": "지원되지 않는 파일 형식입니다. (CSV 또는 JSON만 가능)"}), 400

        count = insert_many_quizzes(quiz_list)
        return jsonify({"message": f"{count}개의 퀴즈가 저장되었습니다."}), 200

    except Exception as e:
        return jsonify({"error": f"처리 중 오류 발생: {str(e)}"}), 500



@quiz_bp.route("/quizzes/<int:quiz_id>", methods=["GET"])
def get_quiz_by_id_route(quiz_id):
    result, status = get_quiz_by_id(quiz_id)
    return jsonify(result), status



@quiz_bp.route("/quizzes", methods=["GET"])
def get_quizzes_by_amino_acid_route():
    amino_acid = request.args.get("amino_acid")
    if not amino_acid:
        return jsonify({"error": "amino_acid 파라미터가 필요합니다."}), 400

    result, status = get_quizzes_by_amino_acid(amino_acid)
    return jsonify(result), status