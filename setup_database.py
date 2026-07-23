import pymysql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# TiDB connection details
host = os.getenv('TIDB_HOST')
port = int(os.getenv('TIDB_PORT'))
user = os.getenv('TIDB_USER')
password = os.getenv('TIDB_PASSWORD')

print(f"Connecting to TiDB at {host}:{port} as {user}")

try:
    # Connect to TiDB without specifying database
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        ssl_verify_cert=True,
        ssl_verify_identity=True
    )

    print("[OK] Connected successfully to TiDB!")

    cursor = connection.cursor()

    # Create database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS hotel_management")
    print("[OK] Database 'hotel_management' created/verified")

    # Show databases
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    print("\nAvailable databases:")
    for db in databases:
        print(f"  - {db[0]}")

    cursor.close()
    connection.close()

    print("\n[OK] Database setup complete! You can now run the Flask app.")

except Exception as e:
    print(f"[ERROR] {e}")
    print("\nTroubleshooting tips:")
    print("1. Check your TiDB Cloud cluster is running")
    print("2. Verify credentials in .env file")
    print("3. Check firewall/network settings")
