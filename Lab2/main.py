from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configure the SQLAlchemy database URI using an environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///moto_data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define the MotoData model
class MotoData(db.Model):
    __tablename__ = 'moto_data'
    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(80), nullable=False)
    model = db.Column(db.String(80), nullable=False)
    tip_oferta = db.Column(db.String(80))
    inmatriculare = db.Column(db.String(80))
    stare = db.Column(db.String(80))
    tip_moto = db.Column(db.String(80))
    anul_fabricatiei = db.Column(db.Integer)
    capacitate_cilindrica = db.Column(db.Integer)
    rulaj = db.Column(db.Integer)
    putere = db.Column(db.Integer)
    culoarea = db.Column(db.String(80))
    cutia_de_viteze = db.Column(db.String(80))
    price = db.Column(db.Float)
    currency = db.Column(db.String(10))

# Initialize the database tables
@app.before_first_request
def create_tables():
    db.create_all()

# File upload route
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No file selected"}), 400

    if file and file.filename.endswith('.json'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        return jsonify({"status": "success", "message": f"File '{file.filename}' uploaded successfully!"}), 201

    return jsonify({"status": "error", "message": "Invalid file type, only JSON files are allowed"}), 400

# Add a new entry to the database
@app.route('/create', methods=['POST'])
def create_entry():
    data = request.get_json()
    try:
        entry = MotoData(
            marca=data.get("Marcă"),
            model=data.get("Model"),
            tip_oferta=data.get("Tip ofertă"),
            inmatriculare=data.get("Înmatriculare"),
            stare=data.get("Stare"),
            tip_moto=data.get("Tip moto"),
            anul_fabricatiei=int(data.get("Anul fabricației", 0)),
            capacitate_cilindrica=int(data.get("Capacitate cilindrică", 0)),
            rulaj=int(data.get("Rulaj", 0)),
            putere=int(data.get("Putere (CP)", 0)),
            culoarea=data.get("Culoarea"),
            cutia_de_viteze=data.get("Cutia de viteze"),
            price=float(data.get("Price", 0)),
            currency=data.get("Currency")
        )
        db.session.add(entry)
        db.session.commit()
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
        if entry_id:
            entry = MotoData.query.get(entry_id)
            if entry:
                return jsonify({
                    "id": entry.id,
                    "marca": entry.marca,
                    "model": entry.model,
                    "tip_oferta": entry.tip_oferta,
                    "inmatriculare": entry.inmatriculare,
                    "stare": entry.stare,
                    "tip_moto": entry.tip_moto,
                    "anul_fabricatiei": entry.anul_fabricatiei,
                    "capacitate_cilindrica": entry.capacitate_cilindrica,
                    "rulaj": entry.rulaj,
                    "putere": entry.putere,
                    "culoarea": entry.culoarea,
                    "cutia_de_viteze": entry.cutia_de_viteze,
                    "price": entry.price,
                    "currency": entry.currency
                }), 200
            return jsonify({"status": "error", "message": "Entry not found"}), 404
        else:
            entries = MotoData.query.offset(offset).limit(limit).all()
            return jsonify([{
                "id": entry.id,
                "marca": entry.marca,
                "model": entry.model,
                "tip_oferta": entry.tip_oferta,
                "inmatriculare": entry.inmatriculare,
                "stare": entry.stare,
                "tip_moto": entry.tip_moto,
                "anul_fabricatiei": entry.anul_fabricatiei,
                "capacitate_cilindrica": entry.capacitate_cilindrica,
                "rulaj": entry.rulaj,
                "putere": entry.putere,
                "culoarea": entry.culoarea,
                "cutia_de_viteze": entry.cutia_de_viteze,
                "price": entry.price,
                "currency": entry.currency
            } for entry in entries]), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# Update an entry by ID
@app.route('/update', methods=['PUT'])
def update_entry():
    entry_id = request.args.get('id')
    data = request.get_json()
    entry = MotoData.query.get(entry_id)
    if not entry:
        return jsonify({"status": "error", "message": "Entry not found"}), 404

    try:
        for field, value in data.items():
            setattr(entry, field, value)
        db.session.commit()
        return jsonify({"status": "success", "message": "Entry updated successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# Delete an entry by ID
@app.route('/delete', methods=['DELETE'])
def delete_entry():
    entry_id = request.args.get('id')
    entry = MotoData.query.get(entry_id)
    if not entry:
        return jsonify({"status": "error", "message": "Entry not found"}), 404

    try:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({"status": "success", "message": "Entry deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
