import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

DB_PARAMS = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}

def run_sql(sql_query):
    rows = []
    err = ""

    try:
        with psycopg.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute(sql_query)
                
                if cur.description is not None:
                    rows = cur.fetchall()
                else:
                    conn.commit()
    except Exception as e:
        err = f"Error in Running SQL Query: {e}"
    finally:
        return rows, err