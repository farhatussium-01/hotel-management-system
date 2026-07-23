// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// Get token from localStorage
function getToken() {
    return localStorage.getItem('token');
}

// Set token in localStorage
function setToken(token) {
    localStorage.setItem('token', token);
}

// Remove token from localStorage
function removeToken() {
    localStorage.removeItem('token');
}

// Get user info from localStorage
function getUserInfo() {
    const userInfo = localStorage.getItem('userInfo');
    return userInfo ? JSON.parse(userInfo) : null;
}

// Set user info in localStorage
function setUserInfo(userInfo) {
    localStorage.setItem('userInfo', JSON.stringify(userInfo));
}

// Remove user info from localStorage
function removeUserInfo() {
    localStorage.removeItem('userInfo');
}

// Check if user is authenticated
function isAuthenticated() {
    return !!getToken();
}

// Logout
function logout() {
    removeToken();
    removeUserInfo();
    window.location.href = 'login.html';
}
