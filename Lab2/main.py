import sqlite3

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

