import sqlite3
import json

connection = sqlite3.connect('moto_data.db')
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS moto_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        marca TEXT,
        model TEXT,
        tip_oferta TEXT,
        inmatriculare TEXT,
        stare TEXT,
        tip_moto TEXT,
        anul_fabricatiei INTEGER,
        capacitate_cilindrica INTEGER,
        rulaj INTEGER,
        putere INTEGER,
        culoarea TEXT,
        cutia_de_viteze TEXT,
        price REAL,
        currency TEXT
    )
''')


def load_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as json_file:
        return json.load(json_file)


def insert_data(data):
    for entry in data:
        # Data cleaning to convert string fields into appropriate formats
        anul_fabricatiei = int(entry.get("Anul fabricației", 0))

        # Remove spaces and convert capacity to integer
        capacitate_cilindrica = int(
            entry.get("Capacitate cilindrică", "0 cm³").replace(" cm³", "").replace(" ", "").strip())

        # Remove spaces and convert rulaj to integer
        rulaj = int(entry.get("Rulaj", "0 km").replace(" km", "").replace(" ", "").strip())

        # Remove spaces and convert power to integer
        putere = int(entry.get("Putere (CP)", "0 CP").replace(" CP", "").replace(" ", "").strip())

        # Convert price to float after removing commas and extra spaces
        price = float(entry.get("Price", "0").replace(",", "").strip())

        # Insert the cleaned data into the database
        cursor.execute('''
            INSERT INTO moto_data (marca, model, tip_oferta, inmatriculare, stare, tip_moto,
                                   anul_fabricatiei, capacitate_cilindrica, rulaj, putere,
                                   culoarea, cutia_de_viteze, price, currency)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry.get("Marcă", "N/A"), entry.get("Model", "N/A"), entry.get("Tip ofertă", "N/A"),
            entry.get("Înmatriculare", "N/A"), entry.get("Stare", "N/A"), entry.get("Tip moto", "N/A"),
            anul_fabricatiei, capacitate_cilindrica, rulaj, putere, entry.get("Culoarea", "N/A"),
            entry.get("Cutia de viteze", "N/A"), price, entry.get("Currency", "N/A")
        ))

    # Commit changes to the database
    connection.commit()
    print("Data insertion complete.")


scrapped_data = load_json_data('scrapped_data.json')

insert_data(scrapped_data)

cursor.execute("SELECT * FROM moto_data")
rows = cursor.fetchall()
for row in rows:
    print(row)

connection.close()
