from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import date
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'books.db')

def get_db_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='book'")
    if cursor.fetchone() is None:
        cursor.execute('''
            CREATE TABLE book (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                publisher TEXT NOT NULL,
                name TEXT NOT NULL,
                date TEXT NOT NULL,
                cost REAL NOT NULL
            )
        ''')
        connection.commit()
    else:
        cursor.execute("PRAGMA table_info(book)")
        columns = [row['name'] for row in cursor.fetchall()]
        if 'Cost' in columns and 'cost' not in columns:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS book_temp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    publisher TEXT NOT NULL,
                    name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    cost REAL NOT NULL
                )
            ''')
            cursor.execute(
                "INSERT INTO book_temp (id, publisher, name, date, cost) SELECT id, publisher, name, date, Cost FROM book"
            )
            cursor.execute("DROP TABLE book")
            cursor.execute("ALTER TABLE book_temp RENAME TO book")
            connection.commit()
        elif 'cost' not in columns:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS book (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    publisher TEXT NOT NULL,
                    name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    cost REAL NOT NULL
                )
            ''')
            connection.commit()
    cursor.close()
    connection.close()

def validate_book_payload(payload):
    if payload is None:
        return None, "Request must be JSON"

    required_fields = ("publisher", "name", "date", "cost")
    for field in required_fields:
        if field not in payload:
            return None, f"Missing field: {field}"

    try:
        cost = float(payload["cost"])
    except (TypeError, ValueError):
        return None, "Invalid cost"

    try:
        date.fromisoformat(payload["date"])
    except (TypeError, ValueError):
        return None, "Invalid date format"

    return {
        "publisher": payload["publisher"],
        "name": payload["name"],
        "date": payload["date"],
        "cost": cost
    }, None

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.route('/', methods=['GET'])
def get_books():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM book")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify([dict(row) for row in rows])

@app.route('/create', methods=['POST'])
def create_books():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    new_book, error = validate_book_payload(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO book (publisher, name, date, cost) VALUES (?, ?, ?, ?)",
        (new_book['publisher'], new_book['name'], new_book['date'], new_book['cost'])
    )
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify(new_book), 201

@app.route('/update/<int:id>', methods=['PUT'])
def update_book(id):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    updated_book, error = validate_book_payload(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE book SET publisher=?, name=?, date=?, cost=? WHERE id=?",
        (updated_book['publisher'], updated_book['name'], updated_book['date'], updated_book['cost'], id)
    )
    connection.commit()
    if cursor.rowcount == 0:
        cursor.close()
        connection.close()
        return jsonify({"error": "Book not found"}), 404

    cursor.close()
    connection.close()
    return jsonify({"message": "Book updated successfully", "data": updated_book})

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_book(id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM book WHERE id=?", (id,))
    connection.commit()
    if cursor.rowcount == 0:
        cursor.close()
        connection.close()
        return jsonify({"error": "Book not found"}), 404

    cursor.close()
    connection.close()
    return jsonify({"message": "Book deleted successfully"})

@app.route("/health")
def health():
    return {"status": "healthy"}, 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)
