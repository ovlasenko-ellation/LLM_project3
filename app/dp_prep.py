import os
#from dotenv import load_dotenv
from db import create_tables, get_db_connection

#load_dotenv()
os.environ['RUN_TIMEZONE_CHECK'] = '0'

if __name__ == "__main__":
    print("Initializing database...")
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Drop existing tables if they exist
    try:
        cursor.execute("DROP TABLE IF EXISTS feedback;")
        cursor.execute("DROP TABLE IF EXISTS conversations;")
        conn.commit()
        print("Existing tables dropped.")
    except Exception as e:
        print(f"Error dropping tables: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    # Create new tables
    create_tables()
    print("New tables created successfully.")

#