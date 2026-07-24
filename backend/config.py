import os
from dotenv import load_dotenv

load_dotenv()

# Detect Vercel environment
IS_VERCEL = bool(os.getenv('VERCEL')) or bool(os.getenv('VERCEL_ENV'))

class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # TiDB / MySQL Database Configuration
    TIDB_HOST = os.getenv('TIDB_HOST', '').strip()
    TIDB_PORT = os.getenv('TIDB_PORT', '4000').strip()
    TIDB_USER = os.getenv('TIDB_USER', 'root').strip()
    TIDB_PASSWORD = os.getenv('TIDB_PASSWORD', '').strip()
    TIDB_DATABASE = os.getenv('TIDB_DATABASE', 'hotel_management').strip()

    DATABASE_URL = os.getenv('DATABASE_URL', '').strip()

    if DATABASE_URL:
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        elif DATABASE_URL.startswith("mysql://"):
            DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)
        elif DATABASE_URL.startswith("mysql2://"):
            DATABASE_URL = DATABASE_URL.replace("mysql2://", "mysql+pymysql://", 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    elif TIDB_HOST and TIDB_HOST != 'localhost':
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{TIDB_USER}:{TIDB_PASSWORD}@{TIDB_HOST}:{TIDB_PORT}/{TIDB_DATABASE}?ssl_verify_cert=true&ssl_verify_identity=true"
    elif TIDB_HOST == 'localhost' and not IS_VERCEL:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{TIDB_USER}:{TIDB_PASSWORD}@{TIDB_HOST}:{TIDB_PORT}/{TIDB_DATABASE}"
    else:
        # Fallback to SQLite database in /tmp for Vercel/serverless environments or local fallback
        db_dir = '/tmp' if IS_VERCEL else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(db_dir, 'hotel_management.db').replace('\\', '/')
        if db_path.startswith('/'):
            SQLALCHEMY_DATABASE_URI = f"sqlite:////{db_path.lstrip('/')}"
        else:
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }

    # Application Configuration
    try:
        TAX_RATE = float(os.getenv('TAX_RATE', '0.12'))
    except (ValueError, TypeError):
        TAX_RATE = 0.12

    try:
        PROMO_CODE_SAVE10 = float(os.getenv('PROMO_CODE_SAVE10', '0.10'))
    except (ValueError, TypeError):
        PROMO_CODE_SAVE10 = 0.10

    # File Upload Configuration
    if IS_VERCEL:
        INVOICE_FOLDER = '/tmp/invoices'
    else:
        INVOICE_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'invoices')

    # Ensure invoice folder exists
    try:
        os.makedirs(INVOICE_FOLDER, exist_ok=True)
    except Exception:
        pass


