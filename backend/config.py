import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # TiDB Database Configuration
    TIDB_HOST = os.getenv('TIDB_HOST', 'localhost')
    TIDB_PORT = os.getenv('TIDB_PORT', '4000')
    TIDB_USER = os.getenv('TIDB_USER', 'root')
    TIDB_PASSWORD = os.getenv('TIDB_PASSWORD', '')
    TIDB_DATABASE = os.getenv('TIDB_DATABASE', 'hotel_management')

    # SQLAlchemy Configuration for TiDB (MySQL compatible)
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{TIDB_USER}:{TIDB_PASSWORD}@{TIDB_HOST}:{TIDB_PORT}/{TIDB_DATABASE}?ssl_verify_cert=true&ssl_verify_identity=true"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }

    # Application Configuration
    TAX_RATE = float(os.getenv('TAX_RATE', '0.12'))
    PROMO_CODE_SAVE10 = float(os.getenv('PROMO_CODE_SAVE10', '0.10'))

    # File Upload Configuration
    INVOICE_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'invoices')
