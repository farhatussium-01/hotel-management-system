import pymysql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# TiDB connection details
host = os.getenv('TIDB_HOST', '').strip()
port_env = os.getenv('TIDB_PORT', '4000').strip()
port = int(port_env) if port_env.isdigit() else 4000
user = os.getenv('TIDB_USER', '').strip()
password = os.getenv('TIDB_PASSWORD', '').strip()

if not host or not user:
    print("[ERROR] TIDB_HOST and TIDB_USER must be set in your .env file!")
    print("Please create a .env file from .env.example with your TiDB Cloud credentials.")
    exit(1)

print(f"Connecting to TiDB at {host}:{port} as {user}")

try:
    # Connect to TiDB without specifying database
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        ssl_verify_cert=False,
        ssl_verify_identity=False
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
