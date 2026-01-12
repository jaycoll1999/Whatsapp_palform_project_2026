/**
 * Forms Management
 * Handles Modals, Submissions, and Button States
 */

document.addEventListener('DOMContentLoaded', () => {
    // Attach validation to existing forms on load
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        attachValidation(form);

        // Hijack submit
        form.onsubmit = (e) => handleFormSubmit(e, form);
    });
});

// --- Modal Logic ---

function openModal() {
    const modal = document.getElementById('modal-container');
    if (modal) {
        modal.classList.add('active');

        // Focus first input
        const firstInput = modal.querySelector('input');
        if (firstInput) firstInput.focus();
    }
}

function closeModal() {
    const modal = document.getElementById('modal-container');
    if (modal) {
        modal.classList.remove('active');

        // Optional: Reset form when closing?
        // const form = modal.querySelector('form');
        // if (form) form.reset();
    }
}

// Close on backdrop click
document.addEventListener('click', (e) => {
    const modal = document.getElementById('modal-container');
    if (modal && e.target === modal) {
        closeModal();
    }
});

// Close on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
    }
});


// --- Submission Logic ---

async function handleFormSubmit(event, form) {
    event.preventDefault();

    if (!validateForm(form)) {
        // Shake animation or focus first error?
        const firstError = form.querySelector('.error');
        if (firstError) firstError.focus();
        return;
    }

    const submitBtn = form.querySelector('button[type="submit"]');
    if (!submitBtn) return;

    // Loading State
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = `
        <span style="display:inline-block; animation: spin 1s linear infinite; margin-right: 5px;">⏳</span> 
        Processing...
    `;

    // Simulate API Request
    try {
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Success
        showToast('Success!', 'Operation completed successfully.');

        if (document.getElementById('modal-container')?.classList.contains('active')) {
            closeModal();
        }

        form.reset();

    } catch (error) {
        alert('Something went wrong. Please try again.');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}


// --- Toast Notification (Simple) ---
function showToast(title, message) {
    // create toast element if it doesn't exist
    let toast = document.getElementById('toast-notification');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast-notification';
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #ffffff;
            border-left: 4px solid var(--success);
            padding: 16px;
            border-radius: 4px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            z-index: 200;
            transform: translateY(100px);
            transition: transform 0.3s ease;
            display: flex;
            flex-direction: column;
            min-width: 250px;
        `;
        document.body.appendChild(toast);
    }

    toast.innerHTML = `
        <div style="font-weight: 600; color: #1f2937;">${title}</div>
        <div style="font-size: 0.875rem; color: #6b7280; margin-top: 4px;">${message}</div>
    `;

    // Show
    requestAnimationFrame(() => {
        toast.style.transform = 'translateY(0)';
    });

    // Hide after 3s
    setTimeout(() => {
        toast.style.transform = 'translateY(150px)';
    }, 3000);
}
