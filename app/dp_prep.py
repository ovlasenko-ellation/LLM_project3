import os
#from dotenv import load_dotenv

os.environ['RUN_TIMEZONE_CHECK'] = '0'

from db import create_tables

#load_dotenv()

if __name__ == "__main__":
    print("Initializing database...")
    create_tables()