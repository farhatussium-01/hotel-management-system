// API Helper Functions

// Make API request
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const token = getToken();

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(url, {
            ...options,
            headers,
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }

        return data;
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}

// Authentication API
const authAPI = {
    login: (credentials) => apiRequest('/auth/login', {
        method: 'POST',
        body: JSON.stringify(credentials),
    }),

    register: (userData) => apiRequest('/auth/register', {
        method: 'POST',
        body: JSON.stringify(userData),
    }),

    forgotPassword: (data) => apiRequest('/auth/forgot-password', {
        method: 'POST',
        body: JSON.stringify(data),
    }),

    resetPassword: (data) => apiRequest('/auth/reset-password', {
        method: 'POST',
        body: JSON.stringify(data),
    }),
};

// Rooms API
const roomsAPI = {
    getAll: () => apiRequest('/rooms'),

    getById: (roomId) => apiRequest(`/rooms/${roomId}`),

    create: (roomData) => apiRequest('/rooms', {
        method: 'POST',
        body: JSON.stringify(roomData),
    }),

    update: (roomId, roomData) => apiRequest(`/rooms/${roomId}`, {
        method: 'PUT',
        body: JSON.stringify(roomData),
    }),

    delete: (roomId) => apiRequest(`/rooms/${roomId}`, {
        method: 'DELETE',
    }),

    search: (params) => {
        const queryString = new URLSearchParams(params).toString();
        return apiRequest(`/rooms/search?${queryString}`);
    },
};

// Reservations API
const reservationsAPI = {
    getAll: () => apiRequest('/reservations'),

    getById: (resId) => apiRequest(`/reservations/${resId}`),

    create: (reservationData) => apiRequest('/reservations', {
        method: 'POST',
        body: JSON.stringify(reservationData),
    }),

    checkin: (resId) => apiRequest(`/reservations/${resId}/checkin`, {
        method: 'POST',
    }),

    checkout: (resId, data = {}) => apiRequest(`/reservations/${resId}/checkout`, {
        method: 'POST',
        body: JSON.stringify(data),
    }),

    cancel: (resId) => apiRequest(`/reservations/${resId}/cancel`, {
        method: 'POST',
    }),
};

// Guests API
const guestsAPI = {
    getAll: () => apiRequest('/guests'),

    register: (guestData) => apiRequest('/guests', {
        method: 'POST',
        body: JSON.stringify(guestData),
    }),
};

// Reports API
const reportsAPI = {
    occupancy: () => apiRequest('/reports/occupancy'),

    financial: () => apiRequest('/reports/financial'),
};

// Invoice API
const invoiceAPI = {
    get: (resId) => apiRequest(`/invoices/${resId}`),
};
