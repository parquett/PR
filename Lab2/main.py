from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def get_db_connection():
    connection = sqlite3.connect('moto_data.db')
    connection.row_factory = sqlite3.Row
    return connection

# Add a new entry to the database
@app.route('/create', methods=['POST'])
def create_entry():
    data = request.get_json()
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO moto_data (marca, model, tip_oferta, inmatriculare, stare, tip_moto,
                                       anul_fabricatiei, capacitate_cilindrica, rulaj, putere,
                                       culoarea, cutia_de_viteze, price, currency)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get("Marcă"), data.get("Model"), data.get("Tip ofertă"), data.get("Înmatriculare"),
                data.get("Stare"), data.get("Tip moto"), int(data.get("Anul fabricației", 0)),
                int(data.get("Capacitate cilindrică", 0)), int(data.get("Rulaj", 0)), int(data.get("Putere (CP)", 0)),
                data.get("Culoarea"), data.get("Cutia de viteze"), float(data.get("Price", 0)), data.get("Currency")
            ))
            connection.commit()
        return jsonify({"status": "success", "message": "Entry created successfully!"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# Get all entries or a specific entry by ID
@app.route('/read', methods=['GET'])
def read_entries():
    entry_id = request.args.get('id')
    offset = int(request.args.get('offset', 0))  # Default offset is 0
    limit = int(request.args.get('limit', 10))  # Default limit is 10

    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()

            # Fetch a specific entry if `id` is provided
            if entry_id:
                cursor.execute("SELECT * FROM moto_data WHERE id = ?", (entry_id,))
                entry = cursor.fetchone()
                if entry:
                    return jsonify(dict(entry)), 200
                return jsonify({"status": "error", "message": "Entry not found"}), 404
            else:
                # Fetch entries with pagination
                cursor.execute("SELECT * FROM moto_data LIMIT ? OFFSET ?", (limit, offset))
                entries = cursor.fetchall()
                return jsonify([dict(row) for row in entries]), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# Update an entry by ID
@app.route('/update', methods=['PUT'])
def update_entry():
    entry_id = request.args.get('id')
    data = request.get_json()
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute('''
                UPDATE moto_data SET marca = ?, model = ?, tip_oferta = ?, inmatriculare = ?, 
                stare = ?, tip_moto = ?, anul_fabricatiei = ?, capacitate_cilindrica = ?, rulaj = ?, 
                putere = ?, culoarea = ?, cutia_de_viteze = ?, price = ?, currency = ?
                WHERE id = ?
            ''', (
                data.get("Marcă"), data.get("Model"), data.get("Tip ofertă"), data.get("Înmatriculare"),
                data.get("Stare"), data.get("Tip moto"), int(data.get("Anul fabricației", 0)),
                int(data.get("Capacitate cilindrică", 0)), int(data.get("Rulaj", 0)), int(data.get("Putere (CP)", 0)),
                data.get("Culoarea"), data.get("Cutia de viteze"), float(data.get("Price", 0)), data.get("Currency"),
                entry_id
            ))
            connection.commit()
        return jsonify({"status": "success", "message": "Entry updated successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# Delete an entry by ID
@app.route('/delete', methods=['DELETE'])
def delete_entry():
    entry_id = request.args.get('id')
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM moto_data WHERE id = ?", (entry_id,))
            connection.commit()
        return jsonify({"status": "success", "message": "Entry deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
