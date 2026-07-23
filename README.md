# Hotel Management System

A full-featured web-based Hotel Reservation Management System built with Flask (Python) backend, HTML/CSS/JavaScript frontend, and TiDB database.

## Features

### User Roles
- **Admin**: Full system access including room management, pricing, and reports
- **Staff**: Front desk operations including guest registration, check-in/check-out, and reservations
- **Guest**: Self-service room search, booking, and reservation management

### Core Functionality
- User authentication with JWT tokens
- Password recovery using Date of Birth verification
- Room management (CRUD operations)
- Reservation booking with date validation
- Check-in/Check-out processing
- Automated billing with tax calculation
- Promo code support (SAVE10 = 10% discount)
- Invoice generation
- Occupancy and financial reports
- Guest registry management

## Technology Stack

### Backend
- **Python 3.8+**
- **Flask 3.0.3** - Web framework
- **Flask-SQLAlchemy** - ORM for database operations
- **PyMySQL** - MySQL driver for TiDB connectivity
- **Flask-CORS** - Cross-origin resource sharing
- **JWT** - Token-based authentication
- **Werkzeug** - Password hashing

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling with modern design
- **JavaScript (ES6+)** - Interactive functionality
- **Fetch API** - RESTful API communication

### Database
- **TiDB Cloud** - Distributed SQL database (MySQL compatible)

## Project Structure

```
hotel-management-system/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── models.py           # Database models
│   └── config.py           # Configuration settings
├── frontend/
│   ├── css/
│   │   └── style.css       # Application styles
│   ├── js/
│   │   ├── config.js       # API configuration
│   │   ├── api.js          # API helper functions
│   │   ├── auth.js         # Authentication logic
│   │   ├── admin.js        # Admin dashboard
│   │   ├── staff.js        # Staff dashboard
│   │   └── guest.js        # Guest dashboard
│   └── pages/
│       ├── login.html      # Login page
│       ├── register.html   # Registration page
│       ├── admin.html      # Admin dashboard
│       ├── staff.html      # Staff dashboard
│       └── guest.html      # Guest dashboard
├── static/
│   └── invoices/           # Generated invoice files
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- TiDB Cloud account (free tier available)
- Modern web browser
- Git (optional)

## Installation

### 1. Clone or Download the Repository

```bash
cd hotel-management-system
```

### 2. Set Up Python Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure TiDB Cloud Database

#### Create TiDB Cloud Cluster

1. Go to [TiDB Cloud](https://tidbcloud.com/)
2. Sign up for a free account (if you don't have one)
3. Create a new cluster (choose "Developer Tier" for free)
4. Wait for cluster to be ready (2-3 minutes)
5. Go to cluster connection settings
6. Note down the following information:
   - Host (e.g., gateway01.ap-southeast-1.prod.aws.tidbcloud.com)
   - Port (usually 4000)
   - Username
   - Password

#### Alternative: Local MySQL/TiDB

If you prefer local development, you can use MySQL or local TiDB:

```bash
# For MySQL
TIDB_HOST=localhost
TIDB_PORT=3306
TIDB_USER=root
TIDB_PASSWORD=your_password
```

### 5. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` file with your TiDB credentials:

```env
# TiDB Configuration
TIDB_HOST=your-tidb-host.tidbcloud.com
TIDB_PORT=4000
TIDB_USER=your_username
TIDB_PASSWORD=your_password
TIDB_DATABASE=hotel_management

# Flask Configuration
SECRET_KEY=your-secret-key-change-this-in-production
FLASK_ENV=development
FLASK_DEBUG=True

# Application Configuration
TAX_RATE=0.12
PROMO_CODE_SAVE10=0.10
```

**Important:** Change `SECRET_KEY` to a random string in production!

### 6. Create Database

Connect to your TiDB cluster and create the database:

```sql
CREATE DATABASE hotel_management;
```

Or let the application create it automatically on first run.

### 7. Initialize Database

The application will automatically create tables and seed default data on first run:

**Default Users:**
- Admin: `admin` / `admin123`
- Staff: `staff` / `staff123`

**Default Rooms:**
- Room 101, 102: Single ($1500/night)
- Room 201, 202: Double ($2500/night)
- Room 301: Suite ($5000/night)

## Running the Application

### 1. Start Backend Server

From the project root directory:

```bash
cd hotel-management-system
python backend/app.py
```

The Flask server will start on `http://localhost:5000`

You should see:
```
Database initialized successfully!
 * Running on http://0.0.0.0:5000
```

### 2. Open Frontend

Open your web browser and navigate to:

```
file:///path/to/hotel-management-system/frontend/pages/login.html
```

Or use a simple HTTP server:

**Python:**
```bash
cd frontend
python -m http.server 8000
```

Then open: `http://localhost:8000/pages/login.html`

**Node.js (if installed):**
```bash
cd frontend
npx http-server -p 8000
```

Then open: `http://localhost:8000/pages/login.html`

## Usage Guide

### Login

1. Navigate to the login page
2. Use default credentials:
   - **Admin:** `admin` / `admin123`
   - **Staff:** `staff` / `staff123`
3. Or register a new guest account

### Admin Dashboard

**Features:**
- Add/Edit/Delete rooms
- Update room pricing
- View all reservations
- Cancel reservations
- View occupancy report
- View financial report

**Common Tasks:**
1. **Add Room:** Click "Add New Room" → Fill form → Save
2. **Update Pricing:** Click "Edit" on room → Change rate → Save
3. **View Reports:** Navigate to Reports → Click "Load Report"

### Staff Dashboard

**Features:**
- Register guests
- View guest registry
- Book rooms for guests
- Check-in guests
- Check-out guests (with billing)
- View/cancel reservations
- Reprint invoices

**Common Tasks:**
1. **Register Guest:** Click "Register New Guest" → Fill form with valid email (@gmail.com or @diu.edu.bd)
2. **Book Room:** Click "Book Room" → Enter guest name, room ID, dates
3. **Check-in:** Navigate to Check-in → Click "Check-in" for booked reservation
4. **Check-out:** Navigate to Check-out → Click "Check-out" → Enter promo code (optional) → Process

### Guest Dashboard

**Features:**
- Search available rooms
- Book rooms
- View own reservations
- Cancel bookings
- View invoices

**Common Tasks:**
1. **Search Rooms:** Select type/status filters → Click "Search"
2. **Book Room:** Enter room ID, check-in/out dates → Click "Reserve"
3. **Cancel Booking:** Navigate to "My Reservations" → Click "Cancel" on booked reservation

## API Documentation

### Authentication

**Login**
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Register**
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "newuser",
  "password": "password123",
  "dob": "2000-01-01"
}
```

### Rooms

**Get All Rooms**
```http
GET /api/rooms
Authorization: Bearer <token>
```

**Create Room (Admin only)**
```http
POST /api/rooms
Authorization: Bearer <token>
Content-Type: application/json

{
  "room_id": 103,
  "type": "Single",
  "rate": 1500.00,
  "status": "Available"
}
```

### Reservations

**Create Reservation**
```http
POST /api/reservations
Authorization: Bearer <token>
Content-Type: application/json

{
  "room_id": 101,
  "guest_name": "John Doe",
  "checkin": "2026-07-25",
  "checkout": "2026-07-27"
}
```

**Check-out Guest**
```http
POST /api/reservations/{res_id}/checkout
Authorization: Bearer <token>
Content-Type: application/json

{
  "promo_code": "SAVE10"
}
```

## Business Rules

### Room Management
- Room IDs must be unique
- Cannot delete rooms with active reservations
- Room status: Available or Occupied

### Reservations
- Check-out date must be after check-in date
- Cannot book rooms with overlapping dates
- Reservation status flow: Booked → CheckedIn → CheckedOut
- Guests can only view/cancel their own reservations

### Billing
- Minimum stay: 1 night
- Tax rate: 12% (configurable)
- Promo code "SAVE10": 10% discount
- Formula: (Nights × Rate + Tax) - Discount

### Guest Registry
- Email must end with @gmail.com or @diu.edu.bd
- Required fields: name, phone, email

## Troubleshooting

### Backend Issues

**Database Connection Error**
```
Error: Can't connect to MySQL server
```
**Solution:** Check `.env` file credentials and TiDB cluster status

**Import Error**
```
ModuleNotFoundError: No module named 'flask'
```
**Solution:** Activate virtual environment and install requirements:
```bash
pip install -r requirements.txt
```

**Port Already in Use**
```
OSError: [Errno 48] Address already in use
```
**Solution:** Kill process using port 5000 or change port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Frontend Issues

**CORS Error**
```
Access to fetch has been blocked by CORS policy
```
**Solution:** Ensure Flask-CORS is installed and backend is running

**Token Expired**
```
Error: Token has expired
```
**Solution:** Log out and log in again (tokens expire after 24 hours)

**API Connection Failed**
```
Failed to fetch
```
**Solution:** Check backend server is running on `http://localhost:5000`

### Database Issues

**Table doesn't exist**
```
Error: Table 'hotel_management.users' doesn't exist
```
**Solution:** Restart backend to trigger database initialization

**SSL Certificate Error**
```
SSL: CERTIFICATE_VERIFY_FAILED
```
**Solution:** For development, modify connection string in `config.py`:
```python
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{TIDB_USER}:{TIDB_PASSWORD}@{TIDB_HOST}:{TIDB_PORT}/{TIDB_DATABASE}?ssl_verify_cert=false"
```

## Development

### Adding New Features

1. **Backend (API endpoint):**
   - Add route in `backend/app.py`
   - Update models in `backend/models.py` if needed

2. **Frontend:**
   - Add API function in `frontend/js/api.js`
   - Update HTML in `frontend/pages/`
   - Add JavaScript logic in respective dashboard file

### Database Schema Changes

1. Modify models in `backend/models.py`
2. Delete existing database or tables
3. Restart application to recreate with new schema

### Security Considerations

**Production Deployment:**
- Change `SECRET_KEY` to a strong random string
- Set `FLASK_ENV=production`
- Set `FLASK_DEBUG=False`
- Use HTTPS for all connections
- Enable TiDB SSL certificate verification
- Implement rate limiting
- Add input sanitization
- Use environment variables for all sensitive data

## Testing

### Manual Testing Checklist

- [ ] User registration and login
- [ ] Password recovery flow
- [ ] Room CRUD operations (admin)
- [ ] Room search and filtering
- [ ] Reservation booking
- [ ] Date validation for reservations
- [ ] Check-in process
- [ ] Check-out with billing
- [ ] Promo code application
- [ ] Invoice generation
- [ ] Reservation cancellation
- [ ] Guest registration
- [ ] Occupancy report
- [ ] Financial report

### Test Accounts

```
Admin:
  Username: admin
  Password: admin123

Staff:
  Username: staff
  Password: staff123

Guest (create your own):
  Register at /pages/register.html
```

## Deployment

### Backend Deployment (Example: Heroku)

1. Create `Procfile`:
```
web: python backend/app.py
```

2. Deploy:
```bash
heroku create hotel-management-app
git push heroku main
```

### Frontend Deployment (Example: Netlify)

1. Update `API_BASE_URL` in `frontend/js/config.js`
2. Deploy `frontend` folder to Netlify
3. Configure environment variables

## License

This project is developed for educational purposes.

## Support

For issues and questions:
- Check troubleshooting section
- Review API documentation
- Check TiDB Cloud documentation: https://docs.pingcap.com/tidbcloud/

## Changelog

### Version 1.0.0 (2026-07-23)
- Initial release
- User authentication with JWT
- Room management
- Reservation system
- Billing and invoicing
- Reports
- Guest registry
- Responsive UI design

## Credits

Based on the original C-language Hotel Management System (HMS-2) with modern web technologies.

---

**Happy Hotel Management!** 🏨
