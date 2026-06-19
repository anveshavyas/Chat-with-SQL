"""
sqlite.py
Run once to create student.db with sample STUDENT data.
Usage: python sqlite.py
"""

import sqlite3
import os

DB_PATH = "student.db"


def create_and_seed():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS STUDENT")

    cursor.execute("""
        CREATE TABLE STUDENT (
            NAME    VARCHAR(25),
            CLASS   VARCHAR(25),
            SECTION VARCHAR(25),
            MARKS   INT
        )
    """)

    students = [
        ("Krish",   "Data Science", "A", 90),
        ("John",    "Data Science", "B", 100),
        ("Mukesh",  "Data Science", "A", 86),
        ("Jacob",   "DEVOPS",       "A", 50),
        ("Dipesh",  "DEVOPS",       "A", 35),
        ("Ananya",  "Data Science", "C", 78),
        ("Ravi",    "DEVOPS",       "B", 62),
        ("Priya",   "Data Science", "B", 95),
        ("Sanjay",  "DEVOPS",       "C", 71),
        ("Neha",    "Data Science", "A", 88),
        ("Arjun",   "DEVOPS",       "B", 45),
        ("Sneha",   "Data Science", "C", 82),
    ]

    cursor.executemany(
        "INSERT INTO STUDENT VALUES (?, ?, ?, ?)",
        students
    )

    conn.commit()
    conn.close()
    print(f"✅ Created {DB_PATH} with {len(students)} student records.")


if __name__ == "__main__":
    create_and_seed()