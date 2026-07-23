from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from models import db, User, Room, Reservation, Guest
from config import Config
from datetime import datetime, timedelta
from functools import wraps
from invoice_generator import generate_invoice_pdf
import jwt
import os

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

db.init_app(app)

# Create invoice directory if it doesn't exist
os.makedirs(app.config['INVOICE_FOLDER'], exist_ok=True)

# JWT token decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(username=data['username']).first()
            if not current_user or not current_user.active:
                return jsonify({'error': 'Invalid token'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(current_user, *args, **kwargs)
    return decorated

# Role-based access control decorator
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            if current_user.role not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(current_user, *args, **kwargs)
        return decorated
    return decorator

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    # Validate required fields
    required_fields = ['username', 'password', 'dob']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'{field} is required'}), 400

    # Check if username already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400

    try:
        # Create new user (guest role by default)
        user = User(
            username=data['username'],
            role=data.get('role', 'guest'),
            dob=datetime.strptime(data['dob'], '%Y-%m-%d').date(),
            active=True
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'User registered successfully', 'user': user.to_dict()}), 201
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.active or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401

    # Generate JWT token
    token = jwt.encode({
        'username': user.username,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({
        'token': token,
        'user': user.to_dict()
    }), 200

@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('dob'):
        return jsonify({'error': 'Username and date of birth are required'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
        if user.dob != dob:
            return jsonify({'error': 'Date of birth does not match'}), 400

        # Return success without exposing user info
        return jsonify({'message': 'Identity verified', 'username': user.username}), 200
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('dob') or not data.get('new_password'):
        return jsonify({'error': 'Username, date of birth, and new password are required'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
        if user.dob != dob:
            return jsonify({'error': 'Date of birth does not match'}), 400

        user.set_password(data['new_password'])
        db.session.commit()

        return jsonify({'message': 'Password reset successfully'}), 200
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== ROOM MANAGEMENT ROUTES ====================

@app.route('/api/rooms', methods=['GET'])
@token_required
def get_rooms(current_user):
    rooms = Room.query.filter_by(active=True).all()
    return jsonify([room.to_dict() for room in rooms]), 200

@app.route('/api/rooms/<int:room_id>', methods=['GET'])
@token_required
def get_room(current_user, room_id):
    room = Room.query.filter_by(room_id=room_id, active=True).first()
    if not room:
        return jsonify({'error': 'Room not found'}), 404
    return jsonify(room.to_dict()), 200

@app.route('/api/rooms', methods=['POST'])
@token_required
@role_required('admin')
def add_room(current_user):
    data = request.get_json()

    required_fields = ['room_id', 'type', 'rate']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    # Check if room_id already exists
    if Room.query.filter_by(room_id=data['room_id']).first():
        return jsonify({'error': 'Room ID already exists'}), 400

    try:
        room = Room(
            room_id=data['room_id'],
            type=data['type'],
            rate=float(data['rate']),
            status=data.get('status', 'Available'),
            active=True
        )

        db.session.add(room)
        db.session.commit()

        return jsonify({'message': 'Room added successfully', 'room': room.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/rooms/<int:room_id>', methods=['PUT'])
@token_required
@role_required('admin')
def update_room(current_user, room_id):
    room = Room.query.filter_by(room_id=room_id, active=True).first()
    if not room:
        return jsonify({'error': 'Room not found'}), 404

    data = request.get_json()

    try:
        if 'type' in data:
            room.type = data['type']
        if 'rate' in data:
            room.rate = float(data['rate'])
        if 'status' in data:
            room.status = data['status']

        db.session.commit()

        return jsonify({'message': 'Room updated successfully', 'room': room.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/rooms/<int:room_id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_room(current_user, room_id):
    room = Room.query.filter_by(room_id=room_id, active=True).first()
    if not room:
        return jsonify({'error': 'Room not found'}), 404

    # Check for active reservations
    active_reservations = Reservation.query.filter_by(
        room_id=room_id,
        active=True
    ).filter(
        Reservation.status.in_(['Booked', 'CheckedIn'])
    ).first()

    if active_reservations:
        return jsonify({'error': 'Cannot delete room with active reservations'}), 400

    try:
        room.active = False
        db.session.commit()

        return jsonify({'message': 'Room deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/rooms/search', methods=['GET'])
@token_required
def search_rooms(current_user):
    room_type = request.args.get('type')
    status = request.args.get('status')

    query = Room.query.filter_by(active=True)

    if room_type:
        query = query.filter_by(type=room_type)
    if status:
        query = query.filter_by(status=status)

    rooms = query.all()
    return jsonify([room.to_dict() for room in rooms]), 200

# ==================== RESERVATION MANAGEMENT ROUTES ====================

@app.route('/api/reservations', methods=['GET'])
@token_required
def get_reservations(current_user):
    if current_user.role == 'guest':
        # Guests can only see their own reservations
        reservations = Reservation.query.filter_by(
            guest_name=current_user.username,
            active=True
        ).all()
    else:
        # Admin and staff can see all reservations
        reservations = Reservation.query.filter_by(active=True).all()

    return jsonify([res.to_dict() for res in reservations]), 200

@app.route('/api/reservations/<int:res_id>', methods=['GET'])
@token_required
def get_reservation(current_user, res_id):
    reservation = Reservation.query.filter_by(res_id=res_id, active=True).first()
    if not reservation:
        return jsonify({'error': 'Reservation not found'}), 404

    # Guests can only view their own reservations
    if current_user.role == 'guest' and reservation.guest_name != current_user.username:
        return jsonify({'error': 'Access denied'}), 403

    return jsonify(reservation.to_dict()), 200

def check_room_availability(room_id, checkin, checkout, ignore_res_id=None):
    """Check if a room is available for the given date range"""
    overlapping = Reservation.query.filter_by(
        room_id=room_id,
        active=True
    ).filter(
        Reservation.status.in_(['Booked', 'CheckedIn'])
    ).filter(
        Reservation.checkin < checkout,
        Reservation.checkout > checkin
    )

    if ignore_res_id:
        overlapping = overlapping.filter(Reservation.res_id != ignore_res_id)

    return overlapping.first() is None

@app.route('/api/reservations', methods=['POST'])
@token_required
def create_reservation(current_user):
    data = request.get_json()

    required_fields = ['room_id', 'checkin', 'checkout']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    # Validate room exists
    room = Room.query.filter_by(room_id=data['room_id'], active=True).first()
    if not room:
        return jsonify({'error': 'Room not found'}), 404

    try:
        checkin = datetime.strptime(data['checkin'], '%Y-%m-%d').date()
        checkout = datetime.strptime(data['checkout'], '%Y-%m-%d').date()

        # Validate dates
        if checkout <= checkin:
            return jsonify({'error': 'Checkout date must be after checkin date'}), 400

        # Check availability
        if not check_room_availability(data['room_id'], checkin, checkout):
            return jsonify({'error': 'Room is not available for selected dates'}), 400

        # Determine guest name
        if current_user.role == 'guest':
            guest_name = current_user.username
        else:
            guest_name = data.get('guest_name', current_user.username)

        # Generate next reservation ID
        max_res = db.session.query(db.func.max(Reservation.res_id)).scalar()
        next_res_id = (max_res or 0) + 1

        reservation = Reservation(
            res_id=next_res_id,
            room_id=data['room_id'],
            guest_name=guest_name,
            checkin=checkin,
            checkout=checkout,
            status='Booked',
            total_amount=0.0,
            active=True
        )

        db.session.add(reservation)
        db.session.commit()

        return jsonify({'message': 'Reservation created successfully', 'reservation': reservation.to_dict()}), 201
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/reservations/<int:res_id>/checkin', methods=['POST'])
@token_required
@role_required('admin', 'staff')
def checkin_guest(current_user, res_id):
    reservation = Reservation.query.filter_by(res_id=res_id, active=True).first()
    if not reservation:
        return jsonify({'error': 'Reservation not found'}), 404

    if reservation.status != 'Booked':
        return jsonify({'error': 'Only Booked reservations can check in'}), 400

    try:
        reservation.status = 'CheckedIn'

        # Update room status
        room = Room.query.filter_by(room_id=reservation.room_id).first()
        if room:
            room.status = 'Occupied'

        db.session.commit()

        return jsonify({'message': 'Guest checked in successfully', 'reservation': reservation.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/reservations/<int:res_id>/checkout', methods=['POST'])
@token_required
@role_required('admin', 'staff')
def checkout_guest(current_user, res_id):
    reservation = Reservation.query.filter_by(res_id=res_id, active=True).first()
    if not reservation:
        return jsonify({'error': 'Reservation not found'}), 404

    if reservation.status != 'CheckedIn':
        return jsonify({'error': 'Only CheckedIn guests can checkout'}), 400

    room = Room.query.filter_by(room_id=reservation.room_id).first()
    if not room:
        return jsonify({'error': 'Room not found'}), 404

    try:
        # Calculate billing
        nights = (reservation.checkout - reservation.checkin).days
        if nights < 1:
            nights = 1

        subtotal = nights * room.rate
        tax_amount = subtotal * app.config['TAX_RATE']

        # Apply promo code if provided
        data = request.get_json() or {}
        promo_code = data.get('promo_code', '')
        discount_amount = 0.0

        if promo_code.upper() == 'SAVE10':
            discount_amount = subtotal * app.config['PROMO_CODE_SAVE10']

        total = subtotal + tax_amount - discount_amount

        # Update reservation
        reservation.status = 'CheckedOut'
        reservation.total_amount = total

        # Update room status
        room.status = 'Available'

        db.session.commit()

        # Generate invoice
        invoice_data = {
            'res_id': reservation.res_id,
            'guest_name': reservation.guest_name,
            'room_id': room.room_id,
            'room_type': room.type,
            'checkin': reservation.checkin.strftime('%Y-%m-%d'),
            'checkout': reservation.checkout.strftime('%Y-%m-%d'),
            'nights': nights,
            'rate': room.rate,
            'subtotal': subtotal,
            'tax_rate': app.config['TAX_RATE'] * 100,
            'tax_amount': tax_amount,
            'discount': discount_amount,
            'total': total
        }

        # Save text invoice to file
        invoice_txt_path = os.path.join(app.config['INVOICE_FOLDER'], f'invoice_{res_id}.txt')
        with open(invoice_txt_path, 'w') as f:
            f.write("=" * 50 + "\n")
            f.write("              INVOICE\n")
            f.write("=" * 50 + "\n")
            f.write(f"Reservation ID   : {invoice_data['res_id']}\n")
            f.write(f"Guest Name       : {invoice_data['guest_name']}\n")
            f.write(f"Room ID / Type   : {invoice_data['room_id']} ({invoice_data['room_type']})\n")
            f.write(f"Check-in         : {invoice_data['checkin']}\n")
            f.write(f"Check-out        : {invoice_data['checkout']}\n")
            f.write(f"Nights Stayed    : {invoice_data['nights']}\n")
            f.write(f"Nightly Rate     : {invoice_data['rate']:.2f}\n")
            f.write("-" * 50 + "\n")
            f.write(f"Subtotal         : {invoice_data['subtotal']:.2f}\n")
            f.write(f"Tax ({invoice_data['tax_rate']:.0f}%)        : {invoice_data['tax_amount']:.2f}\n")
            f.write(f"Discount         : -{invoice_data['discount']:.2f}\n")
            f.write("-" * 50 + "\n")
            f.write(f"TOTAL DUE        : {invoice_data['total']:.2f}\n")
            f.write("=" * 50 + "\n")

        # Generate PDF invoice
        invoice_pdf_path = os.path.join(app.config['INVOICE_FOLDER'], f'invoice_{res_id}.pdf')
        try:
            generate_invoice_pdf(invoice_data, invoice_pdf_path)
        except Exception as pdf_error:
            print(f"Warning: Could not generate PDF invoice: {pdf_error}")

        return jsonify({
            'message': 'Guest checked out successfully',
            'reservation': reservation.to_dict(),
            'invoice': invoice_data
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/reservations/<int:res_id>/cancel', methods=['POST'])
@token_required
def cancel_reservation(current_user, res_id):
    reservation = Reservation.query.filter_by(res_id=res_id, active=True).first()
    if not reservation:
        return jsonify({'error': 'Reservation not found'}), 404

    # Guests can only cancel their own reservations
    if current_user.role == 'guest' and reservation.guest_name != current_user.username:
        return jsonify({'error': 'You can only cancel your own reservations'}), 403

    if reservation.status in ['Cancelled', 'CheckedOut']:
        return jsonify({'error': 'Cannot cancel this reservation'}), 400

    try:
        was_checked_in = reservation.status == 'CheckedIn'
        reservation.status = 'Cancelled'

        # If was checked in, make room available
        if was_checked_in:
            room = Room.query.filter_by(room_id=reservation.room_id).first()
            if room:
                room.status = 'Available'

        db.session.commit()

        return jsonify({'message': 'Reservation cancelled successfully', 'reservation': reservation.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== GUEST MANAGEMENT ROUTES ====================

@app.route('/api/guests', methods=['GET'])
@token_required
@role_required('admin', 'staff')
def get_guests(current_user):
    guests = Guest.query.all()
    return jsonify([guest.to_dict() for guest in guests]), 200

@app.route('/api/guests', methods=['POST'])
@token_required
@role_required('admin', 'staff')
def register_guest(current_user):
    data = request.get_json()

    required_fields = ['name', 'phone', 'email']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'{field} is required'}), 400

    # Validate email
    email = data['email'].lower()
    if not (email.endswith('@gmail.com') or email.endswith('@diu.edu.bd')):
        return jsonify({'error': 'Email must end with @gmail.com or @diu.edu.bd'}), 400

    try:
        guest = Guest(
            name=data['name'],
            phone=data['phone'],
            email=email
        )

        db.session.add(guest)
        db.session.commit()

        return jsonify({'message': 'Guest registered successfully', 'guest': guest.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== REPORTS ROUTES ====================

@app.route('/api/reports/occupancy', methods=['GET'])
@token_required
@role_required('admin')
def occupancy_report(current_user):
    total_rooms = Room.query.filter_by(active=True).count()
    occupied_rooms = Room.query.filter_by(active=True, status='Occupied').count()
    available_rooms = total_rooms - occupied_rooms

    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0

    return jsonify({
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'available_rooms': available_rooms,
        'occupancy_rate': round(occupancy_rate, 1)
    }), 200

@app.route('/api/reports/financial', methods=['GET'])
@token_required
@role_required('admin')
def financial_report(current_user):
    completed_reservations = Reservation.query.filter_by(
        active=True,
        status='CheckedOut'
    ).all()

    total_revenue = sum(res.total_amount for res in completed_reservations)
    completed_stays = len(completed_reservations)
    average_revenue = (total_revenue / completed_stays) if completed_stays > 0 else 0

    return jsonify({
        'completed_stays': completed_stays,
        'total_revenue': round(total_revenue, 2),
        'average_revenue': round(average_revenue, 2)
    }), 200

@app.route('/api/invoices/<int:res_id>', methods=['GET'])
@token_required
def get_invoice(current_user, res_id):
    reservation = Reservation.query.filter_by(res_id=res_id, active=True).first()
    if not reservation:
        return jsonify({'error': 'Reservation not found'}), 404

    if reservation.status != 'CheckedOut':
        return jsonify({'error': 'Invoice only available for checked-out reservations'}), 400

    # Check permissions
    if current_user.role == 'guest' and reservation.guest_name != current_user.username:
        return jsonify({'error': 'Access denied'}), 403

    invoice_path = os.path.join(app.config['INVOICE_FOLDER'], f'invoice_{res_id}.txt')

    if os.path.exists(invoice_path):
        return send_file(invoice_path, mimetype='text/plain', as_attachment=False)
    else:
        return jsonify({'error': 'Invoice file not found'}), 404

@app.route('/api/invoices/<int:res_id>/download', methods=['GET'])
@token_required
def download_invoice_pdf(current_user, res_id):
    reservation = Reservation.query.filter_by(res_id=res_id, active=True).first()
    if not reservation:
        return jsonify({'error': 'Reservation not found'}), 404

    if reservation.status != 'CheckedOut':
        return jsonify({'error': 'Invoice only available for checked-out reservations'}), 400

    # Check permissions
    if current_user.role == 'guest' and reservation.guest_name != current_user.username:
        return jsonify({'error': 'Access denied'}), 403

    invoice_pdf_path = os.path.join(app.config['INVOICE_FOLDER'], f'invoice_{res_id}.pdf')

    if os.path.exists(invoice_pdf_path):
        return send_file(
            invoice_pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'invoice_{res_id}.pdf'
        )
    else:
        return jsonify({'error': 'PDF invoice not found'}), 404

# ==================== INITIALIZATION AND HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Hotel Management System API is running'}), 200

def init_database():
    """Initialize database with default data"""
    with app.app_context():
        db.create_all()

        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                role='admin',
                dob=datetime(2000, 1, 1).date(),
                active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)

        # Check if staff user exists
        staff = User.query.filter_by(username='staff').first()
        if not staff:
            staff = User(
                username='staff',
                role='staff',
                dob=datetime(1995, 5, 5).date(),
                active=True
            )
            staff.set_password('staff123')
            db.session.add(staff)

        # Add default rooms if none exist
        if Room.query.count() == 0:
            default_rooms = [
                Room(room_id=101, type='Single', rate=1500.00, status='Available'),
                Room(room_id=102, type='Single', rate=1500.00, status='Available'),
                Room(room_id=201, type='Double', rate=2500.00, status='Available'),
                Room(room_id=202, type='Double', rate=2500.00, status='Available'),
                Room(room_id=301, type='Suite', rate=5000.00, status='Available'),
            ]
            for room in default_rooms:
                db.session.add(room)

        db.session.commit()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)
