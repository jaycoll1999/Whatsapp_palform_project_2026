const API_BASE = 'http://localhost:8000';

window.addEventListener('page-loaded', (e) => {
    if (e.detail.page === 'resellers') {
        initResellersPage();
    }
});

function initResellersPage() {
    console.log('Resellers Page Initialized');
    loadResellers();

    const form = document.getElementById('reseller-form');
    if (form) {
        form.removeEventListener('submit', handleCreateReseller); // Prevent duplicates if re-init
        form.addEventListener('submit', handleCreateReseller);
    }
}

async function handleCreateReseller(e) {
    e.preventDefault();
    const form = e.target;
    // Basic UI Feedback
    const btn = form.querySelector('button[type="submit"]');
    const originalText = btn.textContent;
    btn.textContent = 'Creating...';
    btn.disabled = true;

    const formData = new FormData(form);

    // Construct nested JSON object based on schema
    const payload = {
        role: 'reseller',
        status: 'active',
        profile: {
            name: formData.get('name'),
            username: formData.get('username'),
            email: formData.get('email'),
            phone: formData.get('phone'),
            password: formData.get('password')
        },
        business: {
            business_name: formData.get('business_name'),
            business_description: '',
            erp_system: formData.get('erp_system'),
            gstin: formData.get('gstin')
        },
        address: {
            full_address: formData.get('full_address'),
            pincode: '',
            country: formData.get('country')
        },
        bank: {
            bank_name: formData.get('bank_name')
        },
        wallet: {
            total_credits: 0,
            available_credits: 0,
            used_credits: 0
        }
    };

    try {
        const response = await fetch(`${API_BASE}/resellers`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const err = await response.json();
            alert(`Error: ${err.detail || 'Failed to create reseller'}`);
            return;
        }

        alert('Reseller created successfully!');
        form.reset();
        loadResellers(); // Refresh list

    } catch (error) {
        console.error('Error creating reseller:', error);
        alert('Network error occurred. Ensure backend is running.');
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

async function loadResellers() {
    const tbody = document.getElementById('resellers-table-body');
    if (!tbody) return;

    tbody.innerHTML = '<tr><td colspan="6" style="padding: 1rem; text-align: center;">Loading...</td></tr>';

    try {
        const response = await fetch(`${API_BASE}/resellers`);
        if (!response.ok) throw new Error('Failed to fetch');

        const resellers = await response.json();

        if (resellers.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="padding: 1rem; text-align: center;">No resellers found.</td></tr>';
            return;
        }

        tbody.innerHTML = resellers.map(r => `
            <tr style="border-bottom: 1px solid var(--border-color);">
                <td style="padding: 1rem;">
                    <div style="font-weight: 500;">${r.profile.name}</div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary);">@${r.profile.username}</div>
                </td>
                <td style="padding: 1rem;">
                    <div>${r.business.business_name || '-'}</div>
                </td>
                 <td style="padding: 1rem;">
                    <div>${r.profile.email}</div>
                </td>
                <td style="padding: 1rem;">
                    ${r.wallet?.available_credits || 0} / ${r.wallet?.total_credits || 0}
                </td>
                <td style="padding: 1rem;">
                    <span style="padding: 0.25rem 0.5rem; border-radius: 999px; background: #e6f4ea; color: #1e7e34; font-size: 0.85rem;">
                        ${r.status}
                    </span>
                </td>
                <td style="padding: 1rem; color: var(--text-secondary);">
                    ${r.created_at ? new Date(r.created_at).toLocaleDateString() : '-'}
                </td>
            </tr>
        `).join('');

    } catch (error) {
        console.error('Error loading resellers:', error);
        tbody.innerHTML = '<tr><td colspan="6" style="padding: 1rem; text-align: center; color: red;">Error loading data. Is the backend running?</td></tr>';
    }
}

// Global scope for onclick/debug
window.loadResellers = loadResellers;
