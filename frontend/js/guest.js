// Guest Dashboard JavaScript

// Check authentication
if (!isAuthenticated()) {
    window.location.href = 'login.html';
}

const userInfo = getUserInfo();
if (userInfo.role !== 'guest') {
    alert('Access denied. Guest only.');
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
        case 'search':
            searchRooms();
            break;
        case 'reservations':
            loadMyReservations();
            break;
        case 'book':
            // Booking form is always visible
            break;
    }
}

// ==================== SEARCH ROOMS ====================

async function searchRooms(filters = { status: 'Available' }) {
    try {
        const rooms = await roomsAPI.search(filters);
        displaySearchResults(rooms);
    } catch (error) {
        console.error('Error searching rooms:', error);
        alert('Failed to search rooms: ' + error.message);
    }
}

function displaySearchResults(rooms) {
    const tbody = document.querySelector('#searchRoomsTable tbody');
    tbody.innerHTML = '';

    if (rooms.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No rooms found</td></tr>';
        return;
    }

    rooms.forEach(room => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${room.room_id}</td>
            <td>${room.type}</td>
            <td>$${room.rate.toFixed(2)}</td>
            <td><span class="status-badge status-${room.status.toLowerCase()}">${room.status}</span></td>
            <td class="action-buttons">
                ${room.status === 'Available' ?
                    `<button class="btn btn-sm btn-primary" onclick="selectRoom(${room.room_id})">Select</button>` :
                    '<span style="color: var(--text-secondary);">Not Available</span>'}
            </td>
        `;
        tbody.appendChild(row);
    });
}

document.getElementById('searchRoomsBtn').addEventListener('click', () => {
    const type = document.getElementById('roomTypeFilter').value;
    const status = document.getElementById('roomStatusFilter').value;

    searchRooms({ type, status });
});

// Select room for booking
window.selectRoom = function(roomId) {
    // Switch to book section
    sections.forEach(s => s.classList.remove('active'));
    document.getElementById('book').classList.add('active');

    navLinks.forEach(l => l.classList.remove('active'));
    document.querySelector('a[data-section="book"]').classList.add('active');

    // Pre-fill room ID
    document.getElementById('roomId').value = roomId;

    // Set default dates (today and tomorrow)
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    document.getElementById('checkin').value = today.toISOString().split('T')[0];
    document.getElementById('checkout').value = tomorrow.toISOString().split('T')[0];
};

// ==================== MY RESERVATIONS ====================

async function loadMyReservations() {
    try {
        const reservations = await reservationsAPI.getAll();
        displayMyReservations(reservations);
    } catch (error) {
        console.error('Error loading reservations:', error);
        alert('Failed to load reservations: ' + error.message);
    }
}

function displayMyReservations(reservations) {
    const tbody = document.querySelector('#reservationsTable tbody');
    tbody.innerHTML = '';

    if (reservations.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">You have no reservations</td></tr>';
        return;
    }

    reservations.forEach(res => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${res.res_id}</td>
            <td>${res.room_id}</td>
            <td>${res.checkin}</td>
            <td>${res.checkout}</td>
            <td><span class="status-badge status-${res.status.toLowerCase()}">${res.status}</span></td>
            <td>$${res.total_amount.toFixed(2)}</td>
            <td class="action-buttons">
                ${res.status === 'Booked' ?
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
        loadMyReservations();
    } catch (error) {
        alert('Failed to cancel reservation: ' + error.message);
    }
};

// ==================== BOOK ROOM ====================

const bookingForm = document.getElementById('bookingForm');

bookingForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const errorMessage = document.getElementById('bookingErrorMessage');
    const successMessage = document.getElementById('bookingSuccessMessage');

    errorMessage.classList.remove('show');
    successMessage.classList.remove('show');

    const formData = {
        room_id: parseInt(document.getElementById('roomId').value),
        checkin: document.getElementById('checkin').value,
        checkout: document.getElementById('checkout').value,
    };

    // Validate dates
    const checkinDate = new Date(formData.checkin);
    const checkoutDate = new Date(formData.checkout);

    if (checkoutDate <= checkinDate) {
        errorMessage.textContent = 'Check-out date must be after check-in date';
        errorMessage.classList.add('show');
        return;
    }

    try {
        const result = await reservationsAPI.create(formData);

        successMessage.textContent = `Room reserved successfully! Reservation ID: ${result.reservation.res_id}`;
        successMessage.classList.add('show');

        bookingForm.reset();

        // Refresh reservations
        setTimeout(() => {
            sections.forEach(s => s.classList.remove('active'));
            document.getElementById('reservations').classList.add('active');

            navLinks.forEach(l => l.classList.remove('active'));
            document.querySelector('a[data-section="reservations"]').classList.add('active');

            loadMyReservations();
        }, 2000);
    } catch (error) {
        errorMessage.textContent = error.message;
        errorMessage.classList.add('show');
    }
});

// ==================== VIEW INVOICE ====================

const invoiceModal = document.getElementById('invoiceModal');
const invoiceModalClose = invoiceModal.querySelector('.close');

invoiceModalClose.addEventListener('click', () => {
    invoiceModal.classList.remove('show');
});

window.addEventListener('click', (e) => {
    if (e.target === invoiceModal) {
        invoiceModal.classList.remove('show');
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

        document.getElementById('invoiceContent').textContent = invoiceText;
        invoiceModal.classList.add('show');
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
searchRooms();
