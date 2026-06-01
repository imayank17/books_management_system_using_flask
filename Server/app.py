from flask import Flask, jsonify, request
from flask_cors import CORS
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
    connection.close()

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
    new_book = request.get_json()
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
    updated_book = request.get_json()
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE book SET publisher=?, name=?, date=?, cost=? WHERE id=?",
        (updated_book['publisher'], updated_book['name'], updated_book['date'], updated_book['cost'], id)
    )
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify(updated_book)

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_book(id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM book WHERE id=?", (id,))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({'result': 'Book deleted'})

@app.route("/health")
def health():
    return {"status": "healthy"}, 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)
