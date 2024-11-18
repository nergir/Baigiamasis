import duckdb

# Path to the SQLite file
sqlite_db_path = 'c:/ftp/roger/roger.db'

# Connect to DuckDB (you can specify a file to save or use in-memory)
conn = duckdb.connect()

# Attach the SQLite database to DuckDB
conn.execute(f"INSTALL sqlite_scanner;")
conn.execute(f"LOAD sqlite_scanner;")
conn.execute(f"CALL sqlite_attach('{sqlite_db_path}');")

# List tables available in the attached SQLite database
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
print("Tables in the attached SQLite database:", tables)

# Import data from a specific SQLite table
table_name = 'judejimai'
data = conn.execute(f"SELECT * FROM {table_name};").fetchdf()
print(f"\nData from table '{table_name}':")
print(data)

# (Optional) If you want to bring the data into DuckDB permanently
conn.execute(f"CREATE TABLE duckdb_table AS SELECT * FROM {table_name};")

# Close connection if done
conn.close()
