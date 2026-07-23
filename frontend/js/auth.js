// Authentication JavaScript

// Show/hide message
function showMessage(elementId, message, isError = true) {
    const element = document.getElementById(elementId);
    if (!element) return;

    element.textContent = message;
    element.classList.add('show');

    if (!isError) {
        element.classList.remove('error-message');
        element.classList.add('success-message');
    }

    setTimeout(() => {
        element.classList.remove('show');
    }, 5000);
}

// Hide message
function hideMessage(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.remove('show');
    }
}

// Login Form Handler
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideMessage('errorMessage');

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            const response = await authAPI.login({ username, password });

            // Store token and user info
            setToken(response.token);
            setUserInfo(response.user);

            // Redirect based on role
            const role = response.user.role;
            if (role === 'admin') {
                window.location.href = 'admin.html';
            } else if (role === 'staff') {
                window.location.href = 'staff.html';
            } else {
                window.location.href = 'guest.html';
            }
        } catch (error) {
            showMessage('errorMessage', error.message);
        }
    });
}

// Register Form Handler
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideMessage('errorMessage');
        hideMessage('successMessage');

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        const dob = document.getElementById('dob').value;

        // Validate passwords match
        if (password !== confirmPassword) {
            showMessage('errorMessage', 'Passwords do not match');
            return;
        }

        try {
            await authAPI.register({
                username,
                password,
                dob,
            });

            showMessage('successMessage', 'Registration successful! Redirecting to login...', false);

            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
        } catch (error) {
            showMessage('errorMessage', error.message);
        }
    });
}

// Forgot Password Modal
const forgotPasswordLink = document.getElementById('forgotPasswordLink');
const forgotPasswordModal = document.getElementById('forgotPasswordModal');
const forgotPasswordForm = document.getElementById('forgotPasswordForm');
const resetPasswordForm = document.getElementById('resetPasswordForm');

if (forgotPasswordLink && forgotPasswordModal) {
    const closeBtn = forgotPasswordModal.querySelector('.close');
    let verifiedUsername = '';
    let verifiedDob = '';

    forgotPasswordLink.addEventListener('click', (e) => {
        e.preventDefault();
        forgotPasswordModal.classList.add('show');
        forgotPasswordForm.style.display = 'block';
        resetPasswordForm.style.display = 'none';
        hideMessage('forgotErrorMessage');
        hideMessage('forgotSuccessMessage');
        hideMessage('resetErrorMessage');
    });

    closeBtn.addEventListener('click', () => {
        forgotPasswordModal.classList.remove('show');
        forgotPasswordForm.reset();
        resetPasswordForm.reset();
    });

    window.addEventListener('click', (e) => {
        if (e.target === forgotPasswordModal) {
            forgotPasswordModal.classList.remove('show');
        }
    });

    // Forgot Password Form
    forgotPasswordForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideMessage('forgotErrorMessage');
        hideMessage('forgotSuccessMessage');

        const username = document.getElementById('forgotUsername').value;
        const dob = document.getElementById('forgotDob').value;

        try {
            await authAPI.forgotPassword({ username, dob });

            verifiedUsername = username;
            verifiedDob = dob;

            showMessage('forgotSuccessMessage', 'Identity verified! Please enter your new password.', false);

            setTimeout(() => {
                forgotPasswordForm.style.display = 'none';
                resetPasswordForm.style.display = 'block';
            }, 1500);
        } catch (error) {
            showMessage('forgotErrorMessage', error.message);
        }
    });

    // Reset Password Form
    resetPasswordForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideMessage('resetErrorMessage');

        const newPassword = document.getElementById('newPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        if (newPassword !== confirmPassword) {
            showMessage('resetErrorMessage', 'Passwords do not match');
            return;
        }

        try {
            await authAPI.resetPassword({
                username: verifiedUsername,
                dob: verifiedDob,
                new_password: newPassword,
            });

            alert('Password reset successfully! Please login with your new password.');
            forgotPasswordModal.classList.remove('show');
            forgotPasswordForm.reset();
            resetPasswordForm.reset();
        } catch (error) {
            showMessage('resetErrorMessage', error.message);
        }
    });
}
