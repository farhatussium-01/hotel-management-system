// Admin Dashboard JavaScript

// Check authentication
if (!isAuthenticated()) {
    window.location.href = 'login.html';
}

const userInfo = getUserInfo();
if (userInfo.role !== 'admin') {
    alert('Access denied. Admin only.');
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

        // Update active link
        navLinks.forEach(l => l.classList.remove('active'));
        link.classList.add('active');

        // Show section
        const sectionId = link.getAttribute('data-section');
        sections.forEach(s => s.classList.remove('active'));
        document.getElementById(sectionId).classList.add('active');

        // Load section data
        loadSectionData(sectionId);
    });
});

// Load section data
function loadSectionData(section) {
    switch (section) {
        case 'rooms':
            loadRooms();
            break;
        case 'reservations':
            loadReservations();
            break;
        case 'reports':
            // Reports load on button click
            break;
    }
}

// ==================== ROOM MANAGEMENT ====================

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
                <button class="btn btn-sm btn-primary" onclick="editRoom(${room.room_id})">Edit</button>
                <button class="btn btn-sm btn-danger" onclick="deleteRoom(${room.room_id})">Delete</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Room filters
document.getElementById('filterRoomsBtn').addEventListener('click', () => {
    const type = document.getElementById('roomTypeFilter').value;
    const status = document.getElementById('roomStatusFilter').value;

    loadRooms({ type, status });
});

// Add Room Modal
const roomModal = document.getElementById('roomModal');
const roomForm = document.getElementById('roomForm');
const addRoomBtn = document.getElementById('addRoomBtn');
const roomModalClose = roomModal.querySelector('.close');

addRoomBtn.addEventListener('click', () => {
    document.getElementById('roomModalTitle').textContent = 'Add New Room';
    roomForm.reset();
    document.getElementById('editRoomId').value = '';
    document.getElementById('roomId').disabled = false;
    roomModal.classList.add('show');
});

roomModalClose.addEventListener('click', () => {
    roomModal.classList.remove('show');
});

window.addEventListener('click', (e) => {
    if (e.target === roomModal) {
        roomModal.classList.remove('show');
    }
});

// Edit Room
window.editRoom = async function(roomId) {
    try {
        const room = await roomsAPI.getById(roomId);

        document.getElementById('roomModalTitle').textContent = 'Edit Room';
        document.getElementById('editRoomId').value = room.room_id;
        document.getElementById('roomId').value = room.room_id;
        document.getElementById('roomId').disabled = true;
        document.getElementById('roomType').value = room.type;
        document.getElementById('roomRate').value = room.rate;
        document.getElementById('roomStatus').value = room.status;

        roomModal.classList.add('show');
    } catch (error) {
        alert('Failed to load room: ' + error.message);
    }
};

// Delete Room
window.deleteRoom = async function(roomId) {
    if (!confirm('Are you sure you want to delete this room?')) {
        return;
    }

    try {
        await roomsAPI.delete(roomId);
        alert('Room deleted successfully');
        loadRooms();
    } catch (error) {
        alert('Failed to delete room: ' + error.message);
    }
};

// Room Form Submit
roomForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const editRoomId = document.getElementById('editRoomId').value;
    const formData = {
        room_id: parseInt(document.getElementById('roomId').value),
        type: document.getElementById('roomType').value,
        rate: parseFloat(document.getElementById('roomRate').value),
        status: document.getElementById('roomStatus').value,
    };

    try {
        if (editRoomId) {
            await roomsAPI.update(parseInt(editRoomId), formData);
            alert('Room updated successfully');
        } else {
            await roomsAPI.create(formData);
            alert('Room added successfully');
        }

        roomModal.classList.remove('show');
        loadRooms();
    } catch (error) {
        document.getElementById('roomErrorMessage').textContent = error.message;
        document.getElementById('roomErrorMessage').classList.add('show');
    }
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

// ==================== REPORTS ====================

document.getElementById('loadOccupancyBtn').addEventListener('click', async () => {
    try {
        const report = await reportsAPI.occupancy();

        document.getElementById('totalRooms').textContent = report.total_rooms;
        document.getElementById('occupiedRooms').textContent = report.occupied_rooms;
        document.getElementById('availableRooms').textContent = report.available_rooms;
        document.getElementById('occupancyRate').textContent = report.occupancy_rate + '%';
    } catch (error) {
        alert('Failed to load occupancy report: ' + error.message);
    }
});

document.getElementById('loadFinancialBtn').addEventListener('click', async () => {
    try {
        const report = await reportsAPI.financial();

        document.getElementById('completedStays').textContent = report.completed_stays;
        document.getElementById('totalRevenue').textContent = '$' + report.total_revenue.toFixed(2);
        document.getElementById('averageRevenue').textContent = '$' + report.average_revenue.toFixed(2);
    } catch (error) {
        alert('Failed to load financial report: ' + error.message);
    }
});

// Initial load
loadRooms();
