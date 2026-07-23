// Staff Dashboard JavaScript

// Check authentication
if (!isAuthenticated()) {
    window.location.href = 'login.html';
}

const userInfo = getUserInfo();
if (userInfo.role !== 'staff') {
    alert('Access denied. Staff only.');
    logout();
}

// Display user info
document.getElementById('userInfo').textContent = `Welcome, ${userInfo.username}`;

// Logout handler
document.getElementById('logoutBtn').addEventListener('click', (e) => {
    e.preventDefault();
    logout();
});

// Navigation
const navLinks = document.querySelectorAll('.sidebar-menu a[data-section]');
const sections = document.querySelectorAll('.content-section');

navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();

        navLinks.forEach(l => l.classList.remove('active'));
        link.classList.add('active');

        const sectionId = link.getAttribute('data-section');
        sections.forEach(s => s.classList.remove('active'));
        document.getElementById(sectionId).classList.add('active');

        loadSectionData(sectionId);
    });
});

function loadSectionData(section) {
    switch (section) {
        case 'guests':
            loadGuests();
            break;
        case 'rooms':
            loadRooms();
            break;
        case 'reservations':
            loadReservations();
            break;
        case 'checkin':
            loadCheckinReservations();
            break;
        case 'checkout':
            loadCheckoutReservations();
            break;
    }
}

// ==================== GUEST REGISTRY ====================

async function loadGuests() {
    try {
        const guests = await guestsAPI.getAll();
        displayGuests(guests);
    } catch (error) {
        console.error('Error loading guests:', error);
        alert('Failed to load guests: ' + error.message);
    }
}

function displayGuests(guests) {
    const tbody = document.querySelector('#guestsTable tbody');
    tbody.innerHTML = '';

    if (guests.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" style="text-align: center;">No guests registered</td></tr>';
        return;
    }

    guests.forEach(guest => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${guest.name}</td>
            <td>${guest.phone}</td>
            <td>${guest.email}</td>
        `;
        tbody.appendChild(row);
    });
}

// Register Guest Modal
const guestModal = document.getElementById('guestModal');
const guestForm = document.getElementById('guestForm');
const registerGuestBtn = document.getElementById('registerGuestBtn');
const guestModalClose = guestModal.querySelector('.close');

registerGuestBtn.addEventListener('click', () => {
    guestForm.reset();
    guestModal.classList.add('show');
});

guestModalClose.addEventListener('click', () => {
    guestModal.classList.remove('show');
});

window.addEventListener('click', (e) => {
    if (e.target === guestModal) {
        guestModal.classList.remove('show');
    }
});

guestForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = {
        name: document.getElementById('guestName').value,
        phone: document.getElementById('guestPhone').value,
        email: document.getElementById('guestEmail').value,
    };

    try {
        await guestsAPI.register(formData);
        alert('Guest registered successfully');
        guestModal.classList.remove('show');
        loadGuests();
    } catch (error) {
        document.getElementById('guestErrorMessage').textContent = error.message;
        document.getElementById('guestErrorMessage').classList.add('show');
    }
});

// ==================== ROOMS ====================

async function loadRooms(filters = {}) {
    try {
        let rooms;
        if (filters.type || filters.status) {
            rooms = await roomsAPI.search(filters);
        } else {
            rooms = await roomsAPI.getAll();
        }

        displayRooms(rooms);
    } catch (error) {
        console.error('Error loading rooms:', error);
        alert('Failed to load rooms: ' + error.message);
    }
}

function displayRooms(rooms) {
    const tbody = document.querySelector('#roomsTable tbody');
    tbody.innerHTML = '';

    if (rooms.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align: center;">No rooms found</td></tr>';
        return;
    }

    rooms.forEach(room => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${room.room_id}</td>
            <td>${room.type}</td>
            <td>$${room.rate.toFixed(2)}</td>
            <td><span class="status-badge status-${room.status.toLowerCase()}">${room.status}</span></td>
        `;
        tbody.appendChild(row);
    });
}

document.getElementById('filterRoomsBtn').addEventListener('click', () => {
    const type = document.getElementById('roomTypeFilter').value;
    const status = document.getElementById('roomStatusFilter').value;

    loadRooms({ type, status });
});

// ==================== RESERVATIONS ====================

async function loadReservations() {
    try {
        const reservations = await reservationsAPI.getAll();
        displayReservations(reservations);
    } catch (error) {
        console.error('Error loading reservations:', error);
        alert('Failed to load reservations: ' + error.message);
    }
}

function displayReservations(reservations) {
    const tbody = document.querySelector('#reservationsTable tbody');
    tbody.innerHTML = '';

    if (reservations.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">No reservations found</td></tr>';
        return;
    }

    reservations.forEach(res => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${res.res_id}</td>
            <td>${res.room_id}</td>
            <td>${res.guest_name}</td>
            <td>${res.checkin}</td>
            <td>${res.checkout}</td>
            <td><span class="status-badge status-${res.status.toLowerCase()}">${res.status}</span></td>
            <td>$${res.total_amount.toFixed(2)}</td>
            <td class="action-buttons">
                ${res.status !== 'Cancelled' && res.status !== 'CheckedOut' ?
                    `<button class="btn btn-sm btn-danger" onclick="cancelReservation(${res.res_id})">Cancel</button>` :
                    ''}
                ${res.status === 'CheckedOut' ?
                    `<button class="btn btn-sm btn-primary" onclick="viewInvoice(${res.res_id})">View</button>
                     <button class="btn btn-sm btn-success" onclick="downloadInvoicePDF(${res.res_id})">Download PDF</button>` :
                    ''}
            </td>
        `;
        tbody.appendChild(row);
    });
}

window.cancelReservation = async function(resId) {
    if (!confirm('Are you sure you want to cancel this reservation?')) {
        return;
    }

    try {
        await reservationsAPI.cancel(resId);
        alert('Reservation cancelled successfully');
        loadReservations();
    } catch (error) {
        alert('Failed to cancel reservation: ' + error.message);
    }
};

// Book Room Modal
const bookingModal = document.getElementById('bookingModal');
const bookingForm = document.getElementById('bookingForm');
const bookRoomBtn = document.getElementById('bookRoomBtn');
const bookingModalClose = bookingModal.querySelector('.close');

bookRoomBtn.addEventListener('click', () => {
    bookingForm.reset();
    bookingModal.classList.add('show');
});

bookingModalClose.addEventListener('click', () => {
    bookingModal.classList.remove('show');
});

bookingForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = {
        room_id: parseInt(document.getElementById('bookingRoomId').value),
        guest_name: document.getElementById('bookingGuestName').value,
        checkin: document.getElementById('bookingCheckin').value,
        checkout: document.getElementById('bookingCheckout').value,
    };

    try {
        await reservationsAPI.create(formData);
        alert('Room booked successfully');
        bookingModal.classList.remove('show');
        loadReservations();
    } catch (error) {
        document.getElementById('bookingErrorMessage').textContent = error.message;
        document.getElementById('bookingErrorMessage').classList.add('show');
    }
});

// ==================== CHECK-IN ====================

async function loadCheckinReservations() {
    try {
        const reservations = await reservationsAPI.getAll();
        const bookedReservations = reservations.filter(r => r.status === 'Booked');
        displayCheckinReservations(bookedReservations);
    } catch (error) {
        console.error('Error loading check-in reservations:', error);
        alert('Failed to load check-in reservations: ' + error.message);
    }
}

function displayCheckinReservations(reservations) {
    const tbody = document.querySelector('#checkinTable tbody');
    tbody.innerHTML = '';

    if (reservations.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No reservations ready for check-in</td></tr>';
        return;
    }

    reservations.forEach(res => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${res.res_id}</td>
            <td>${res.room_id}</td>
            <td>${res.guest_name}</td>
            <td>${res.checkin}</td>
            <td class="action-buttons">
                <button class="btn btn-sm btn-success" onclick="checkinGuest(${res.res_id})">Check-in</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

window.checkinGuest = async function(resId) {
    if (!confirm('Check-in this guest?')) {
        return;
    }

    try {
        await reservationsAPI.checkin(resId);
        alert('Guest checked in successfully');
        loadCheckinReservations();
    } catch (error) {
        alert('Failed to check-in guest: ' + error.message);
    }
};

// ==================== CHECK-OUT ====================

async function loadCheckoutReservations() {
    try {
        const reservations = await reservationsAPI.getAll();
        const checkedInReservations = reservations.filter(r => r.status === 'CheckedIn');
        displayCheckoutReservations(checkedInReservations);
    } catch (error) {
        console.error('Error loading check-out reservations:', error);
        alert('Failed to load check-out reservations: ' + error.message);
    }
}

function displayCheckoutReservations(reservations) {
    const tbody = document.querySelector('#checkoutTable tbody');
    tbody.innerHTML = '';

    if (reservations.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No guests ready for check-out</td></tr>';
        return;
    }

    reservations.forEach(res => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${res.res_id}</td>
            <td>${res.room_id}</td>
            <td>${res.guest_name}</td>
            <td>${res.checkout}</td>
            <td class="action-buttons">
                <button class="btn btn-sm btn-success" onclick="openCheckoutModal(${res.res_id})">Check-out</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Checkout Modal
const checkoutModal = document.getElementById('checkoutModal');
const checkoutForm = document.getElementById('checkoutForm');
const checkoutModalClose = checkoutModal.querySelector('.close');

checkoutModalClose.addEventListener('click', () => {
    checkoutModal.classList.remove('show');
});

window.openCheckoutModal = function(resId) {
    document.getElementById('checkoutResId').value = resId;
    document.getElementById('promoCode').value = '';
    document.getElementById('invoiceDisplay').style.display = 'none';
    checkoutModal.classList.add('show');
};

checkoutForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const resId = parseInt(document.getElementById('checkoutResId').value);
    const promoCode = document.getElementById('promoCode').value;

    try {
        const result = await reservationsAPI.checkout(resId, { promo_code: promoCode });

        // Display invoice
        document.getElementById('invoiceDisplay').style.display = 'block';
        const invoiceDetails = document.getElementById('invoiceDetails');

        invoiceDetails.innerHTML = `
            <div style="font-family: monospace; white-space: pre-wrap;">
==================== INVOICE ====================
Reservation ID   : ${result.invoice.res_id}
Guest Name       : ${result.invoice.guest_name}
Room ID / Type   : ${result.invoice.room_id} (${result.invoice.room_type})
Check-in         : ${result.invoice.checkin}
Check-out        : ${result.invoice.checkout}
Nights Stayed    : ${result.invoice.nights}
Nightly Rate     : $${result.invoice.rate.toFixed(2)}
---------------------------------------------------
Subtotal         : $${result.invoice.subtotal.toFixed(2)}
Tax (${result.invoice.tax_rate.toFixed(0)}%)        : $${result.invoice.tax_amount.toFixed(2)}
Discount         : -$${result.invoice.discount.toFixed(2)}
---------------------------------------------------
TOTAL DUE        : $${result.invoice.total.toFixed(2)}
===================================================
            </div>
        `;

        alert('Guest checked out successfully');
        loadCheckoutReservations();
    } catch (error) {
        document.getElementById('checkoutErrorMessage').textContent = error.message;
        document.getElementById('checkoutErrorMessage').classList.add('show');
    }
});

window.viewInvoice = async function(resId) {
    try {
        const response = await fetch(`${API_BASE_URL}/invoices/${resId}`, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to load invoice');
        }

        const invoiceText = await response.text();
        alert(invoiceText);
    } catch (error) {
        alert('Failed to load invoice: ' + error.message);
    }
};

window.downloadInvoicePDF = async function(resId) {
    try {
        const response = await fetch(`${API_BASE_URL}/invoices/${resId}/download`, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to download PDF invoice');
        }

        // Create blob from response
        const blob = await response.blob();

        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `invoice_${resId}.pdf`;
        document.body.appendChild(a);
        a.click();

        // Cleanup
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        console.log('PDF invoice downloaded successfully');
    } catch (error) {
        alert('Failed to download PDF invoice: ' + error.message);
    }
};

// Initial load
loadGuests();
