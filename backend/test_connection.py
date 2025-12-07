import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch variables
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DBNAME = os.getenv("DB_NAME")

print(f"Connecting to: {HOST}:{PORT}/{DBNAME} as {USER}")

# Connect to the database
try:
    connection = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME
    )
    print("✅ Connection successful!")
    
    # Create a cursor to execute SQL queries
    cursor = connection.cursor()
    
    # Test query - get current time
    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()
    print(f"✅ Current Time: {result[0]}")
    
    # Check if tables exist
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    print(f"\n✅ Found {len(tables)} tables:")
    for table in tables:
        print(f"   - {table[0]}")
    
    # Count matches
    cursor.execute("SELECT COUNT(*) FROM matches;")
    match_count = cursor.fetchone()[0]
    print(f"\n✅ Matches in database: {match_count}")

    # Close the cursor and connection
    cursor.close()
    connection.close()
    print("\n✅ Connection closed successfully.")

except Exception as e:
    print(f"❌ Failed to connect: {e}")
