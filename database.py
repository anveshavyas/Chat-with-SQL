"""
database.py
Handles database connections for both SQLite and MySQL.
Returns a LangChain SQLDatabase object.
"""

from langchain_community.utilities import SQLDatabase
import sqlite3
import pandas as pd
import re


def get_sqlite_db(db_path: str = "student.db") -> SQLDatabase:
    """
    Connect to a local SQLite database file.
    Returns a LangChain SQLDatabase instance.
    """
    uri = f"sqlite:///{db_path}"
    db = SQLDatabase.from_uri(uri)
    return db


def _clean_column_name(name: str) -> str:
    """Make a column name SQL-safe."""
    name = str(name).strip()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^0-9a-zA-Z_]", "", name)
    if not name:
        name = "col"
    if name[0].isdigit():
        name = f"_{name}"
    return name


def build_sqlite_from_file(uploaded_file, db_path: str = "uploaded.db", table_name: str = "data") -> SQLDatabase:
    """
    Reads an uploaded CSV or Excel file (Streamlit UploadedFile object),
    loads it into a fresh SQLite database, and returns a LangChain SQLDatabase.

    - uploaded_file: file-like object from st.file_uploader
    - db_path: path to write the SQLite .db file
    - table_name: name of the table to create
    """
    filename = uploaded_file.name.lower()

    if filename.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif filename.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file)
    else:
        raise ValueError("Unsupported file type. Please upload a .csv or .xlsx/.xls file.")

    # Clean column names so the LLM-generated SQL has predictable identifiers
    df.columns = [_clean_column_name(c) for c in df.columns]

    table_name = _clean_column_name(table_name) or "data"

    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()

    return get_sqlite_db(db_path)


def get_mysql_db(
    host: str,
    user: str,
    password: str,
    database: str,
    port: int = 3306,
) -> SQLDatabase:
    """
    Connect to a MySQL database.
    Requires mysql-connector-python installed.
    Returns a LangChain SQLDatabase instance.
    """
    uri = (
        f"mysql+mysqlconnector://{user}:{password}"
        f"@{host}:{port}/{database}"
    )
    db = SQLDatabase.from_uri(uri)
    return db


def get_db_info(db: SQLDatabase) -> dict:
    """
    Returns a dict with table names and their schemas.
    Used by the UI to display the schema explorer.
    """
    tables = db.get_usable_table_names()
    info = {}
    for table in tables:
        info[table] = db.get_table_info(table_names=[table])
    return info