from sqlalchemy import create_engine

# Database connection string
connection_string = "postgresql://myuser:mypassword@localhost:5432/mydatabase"
engine = create_engine(connection_string)

try:
    with engine.connect() as connection:
        print("Connected to the database!")
except Exception as e:
    print("Failed to connect to the database:", e)
