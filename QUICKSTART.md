# Hotel Management System - Quick Start Guide

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Python Dependencies
```bash
cd hotel-management-system
pip install -r requirements.txt
```

### Step 2: Configure TiDB Connection

Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env` with your TiDB Cloud credentials:
```env
TIDB_HOST=your-cluster.tidbcloud.com
TIDB_PORT=4000
TIDB_USER=your_username
TIDB_PASSWORD=your_password
TIDB_DATABASE=hotel_management
SECRET_KEY=change-this-to-random-string
```

**Get TiDB Cloud Free Tier:**
1. Visit: https://tidbcloud.com/
2. Sign up (Free)
3. Create cluster (Developer Tier)
4. Copy connection details

### Step 3: Start Backend
```bash
python backend/app.py
```

Expected output:
```
Database initialized successfully!
 * Running on http://0.0.0.0:5000
```

### Step 4: Open Frontend

**Option A - Direct File:**
```
Open: frontend/pages/login.html in your browser
```

**Option B - Simple Server:**
```bash
cd frontend
python -m http.server 8000
# Then open: http://localhost:8000/pages/login.html
```

### Step 5: Login
```
Username: admin
Password: admin123
```

## 🎯 Test the System

1. **Login as Admin** → Add a new room
2. **Login as Staff** → Register a guest → Book a room
3. **Login as Guest** → Search rooms → Make a reservation

## 📋 Default Credentials

| Role  | Username | Password   |
|-------|----------|------------|
| Admin | admin    | admin123   |
| Staff | staff    | staff123   |
| Guest | Register | New Account|

## ⚡ Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run backend
python backend/app.py

# Run frontend server
cd frontend && python -m http.server 8000
```

## 🔧 Troubleshooting

**Can't connect to database?**
- Check `.env` file has correct TiDB credentials
- Verify TiDB cluster is running

**Module not found?**
- Activate virtual environment: `venv\Scripts\activate` (Windows)
- Install dependencies: `pip install -r requirements.txt`

**Port already in use?**
- Change port in `backend/app.py`: `app.run(port=5001)`

## 📚 Full Documentation

See `README.md` for complete documentation.

---

**Need Help?**
- Review README.md for detailed setup
- Check API documentation in README
- Review troubleshooting section
