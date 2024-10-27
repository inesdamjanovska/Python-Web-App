from flask import Blueprint, request, jsonify
import pandas as pd
from database import get_db_connection
import logging

compute = Blueprint('compute', __name__)
AUTH_PASSPHRASE = "TestPassword123#"

@compute.route('/api/compute', methods=['POST'])
def compute_endpoint():
    auth_passphrase = request.headers.get('Authorization')
    if auth_passphrase != AUTH_PASSPHRASE:
        logging.warning("Unauthorized access attempt.")
        return jsonify({"error": "Unauthorized"}), 401

    if 'file' not in request.files:
        logging.error("No file part in the request.")
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        logging.error("No selected file.")
        return jsonify({"error": "No selected file"}), 400

    if not file.filename.endswith('.csv'):
        logging.error("Invalid file type.")
        return jsonify({"error": "File type not allowed, must be CSV"}), 400

    try:
        df = pd.read_csv(file)
    except Exception as e:
        logging.error(f"Error reading CSV file: {str(e)}")
        return jsonify({"error": f"Error reading CSV file: {str(e)}"}), 400

    required_columns = ['A', 'O', 'B']
    if not all(col in df.columns for col in required_columns):
        logging.error("Invalid CSV structure.")
        return jsonify({"error": f"Invalid CSV structure, must contain columns {', '.join(required_columns)}"}), 400

    addition_results = []
    multiplication_results = []
    subtraction_results = []
    division_results = []

    for _, row in df.iterrows():
        try:
            A = float(row['A'])
            B = float(row['B'])
            O = row['O']
        except ValueError:
            logging.error("Columns A and B must contain numeric values.")
            return jsonify({"error": "Columns A and B must contain numeric values"}), 400
        
        if O == '+':
            addition_results.append(A + B)
        elif O == '*':
            multiplication_results.append(A * B)
        elif O == '-':
            subtraction_results.append(A - B)
        elif O == '/':
            if B == 0:
                logging.error("Division by zero.")
                return jsonify({"error": "Division by zero"}), 400
            division_results.append(A / B)
        else:
            logging.error(f"Unsupported operator: {O}")
            return jsonify({"error": f"Unsupported operator: {O}"}), 400

    final_result = sum(addition_results) + sum(multiplication_results) + sum(subtraction_results) + sum(division_results)

    user_placeholder = "user_example"  
    request_name_placeholder = file.filename

    try:
        conn = get_db_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO requests (user, request_name, file_reference) VALUES (?, ?, ?)',
                (user_placeholder, request_name_placeholder, request_name_placeholder)
            )
            request_id = cursor.lastrowid
            cursor.execute('INSERT INTO results (request_id, result) VALUES (?, ?)', (request_id, final_result))
    except Exception as e:
        logging.error(f"Database error: {str(e)}")
        return jsonify({"error": "Database error"}), 500

    logging.info(f"File processed successfully: {request_name_placeholder}, Result: {final_result}")
    return jsonify({"message": "File processed successfully", "result": final_result}), 200
