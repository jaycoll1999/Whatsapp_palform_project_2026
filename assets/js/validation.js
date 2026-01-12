/**
 * Validation Logic
 * Handles real-time and submission validation with inline feedback.
 */

// Global config for validation rules
const VALIDATION_RULES = {
    required: (value) => value.trim() !== '',
    email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
    minlength: (value, min) => value.length >= min,
    phone: (value) => /^\+?[\d\s-]{10,}$/.test(value) // Basic loose phone check
};

const ERROR_MESSAGES = {
    required: 'This field is required',
    email: 'Please enter a valid email address',
    phone: 'Please enter a valid phone number',
    minlength: (min) => `Must be at least ${min} characters`
};

/**
 * Validates a single input element
 * @param {HTMLElement} input 
 * @returns {boolean} isValid
 */
function validateInput(input) {
    const value = input.value;
    let isValid = true;
    let error = '';

    // Remove existing error state
    clearError(input);

    // Check Required
    if (input.hasAttribute('required') && !VALIDATION_RULES.required(value)) {
        isValid = false;
        error = ERROR_MESSAGES.required;
    }
    // Check Email
    else if (input.type === 'email' && value && !VALIDATION_RULES.email(value)) {
        isValid = false;
        error = ERROR_MESSAGES.email;
    }
    // Check specific types (e.g. Tel)
    else if (input.type === 'tel' && value && !VALIDATION_RULES.phone(value)) {
        isValid = false;
        error = ERROR_MESSAGES.phone;
    }

    if (!isValid) {
        showError(input, error);
    } else {
        showSuccess(input);
    }

    return isValid;
}

/**
 * Shows error message UI
 */
function showError(input, message) {
    input.classList.add('error');

    // Create or update error message element
    let errorEl = input.parentElement.querySelector('.error-msg');
    if (!errorEl) {
        errorEl = document.createElement('div');
        errorEl.className = 'error-msg';
        input.parentElement.appendChild(errorEl);
    }
    errorEl.textContent = message;
}

/**
 * Clears error message UI
 */
function clearError(input) {
    input.classList.remove('error');
    const errorEl = input.parentElement.querySelector('.error-msg');
    if (errorEl) {
        errorEl.remove();
    }
}

/**
 * Optional: Show success state (e.g. green border)
 */
function showSuccess(input) {
    // Only show success if it had content. Empty optional fields shouldn't turn green.
    if (input.value.trim().length > 0) {
        // Maybe add a subtle checkmark or green border?
        // input.style.borderColor = 'var(--success)';
    }
}

/**
 * Validates entire form
 */
function validateForm(form) {
    const inputs = form.querySelectorAll('input, select, textarea');
    let isFormValid = true;

    inputs.forEach(input => {
        if (!validateInput(input)) {
            isFormValid = false;
        }
    });

    return isFormValid;
}

/**
 * Attach listeners to a form for real-time validation
 */
function attachValidation(form) {
    const inputs = form.querySelectorAll('input, select, textarea');

    inputs.forEach(input => {
        // Validate on blur
        input.addEventListener('blur', () => validateInput(input));

        // Clear error on input
        input.addEventListener('input', () => {
            if (input.classList.contains('error')) {
                validateInput(input);
            }
        });
    });
}
