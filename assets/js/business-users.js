const API_BASE = 'http://localhost:8000';

window.addEventListener('page-loaded', (e) => {
    if (e.detail.page === 'business-users') {
        initBusinessUsersPage();
    }
});

function initBusinessUsersPage() {
    console.log('Business Users Page Initialized');

    // Load dropdowns and table
    loadResellersForDropdown();
    loadBusinessUsers();

    const form = document.getElementById('business-user-form');
    if (form) {
        form.removeEventListener('submit', handleCreateBusinessUser);
        form.addEventListener('submit', handleCreateBusinessUser);
    }
}

async function loadResellersForDropdown() {
    const select = document.getElementById('reseller-select');
    if (!select) return;

    try {
        const response = await fetch(`${API_BASE}/resellers`);
        if (!response.ok) throw new Error('Failed to fetch resellers');
        const resellers = await response.json();

        if (resellers.length === 0) {
            select.innerHTML = '<option value="">No Resellers Found</option>';
            return;
        }

        select.innerHTML = '<option value="">Select Reseller</option>' +
            resellers.map(r => `<option value="${r.user_id}">${r.profile.name} (${r.business.business_name || 'No Business'})</option>`).join('');

    } catch (error) {
        console.error('Error loading resellers for dropdown:', error);
        select.innerHTML = '<option value="">Error loading resellers</option>';
    }
}

async function handleCreateBusinessUser(e) {
    e.preventDefault();
    const form = e.target;
    // UI Feedback
    const btn = form.querySelector('button[type="submit"]');
    const originalText = btn.textContent;
    btn.textContent = 'Creating...';
    btn.disabled = true;

    const formData = new FormData(form);

    // Construct nested JSON object
    const payload = {
        role: 'business_owner',
        status: 'active',
        parent_reseller_id: formData.get('parent_reseller_id'),
        whatsapp_mode: formData.get('whatsapp_mode'),
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
            erp_system: formData.get('erp_system') || '',
            gstin: formData.get('gstin')
        },
        address: {
            full_address: formData.get('full_address'),
            pincode: '',
            country: formData.get('country')
        },
        wallet: {
            credits_allocated: 0,
            credits_used: 0,
            credits_remaining: 0
        }
    };

    try {
        const response = await fetch(`${API_BASE}/business-users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const err = await response.json();
            alert(`Error: ${err.detail || 'Failed to create business user'}`);
            return;
        }

        alert('Business User created successfully!');
        form.reset();
        loadBusinessUsers(); // Refresh list

    } catch (error) {
        console.error('Error creating business user:', error);
        alert('Network error occurred.');
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

async function loadBusinessUsers() {
    const tbody = document.getElementById('business-users-table-body');
    if (!tbody) return;

    tbody.innerHTML = '<tr><td colspan="6" style="padding: 1rem; text-align: center;">Loading...</td></tr>';

    try {
        const response = await fetch(`${API_BASE}/business-users`);
        if (!response.ok) throw new Error('Failed to fetch');

        const users = await response.json();

        if (users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="padding: 1rem; text-align: center;">No business users found.</td></tr>';
            return;
        }

        // We fetch resellers to map ID to Name (optional optimization: backend could join this, but for now we fetch client-side or just show ID)
        // For simplicity, we will show the ID or fetch all resellers again to map names if list is small. 
        // Let's just show the ID for now or try to match if we have the list.

        tbody.innerHTML = users.map(u => `
            <tr>
                <td style="padding: 1rem;">
                    <div style="font-weight: 500;">${u.profile.name}</div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary);">@${u.profile.username}</div>
                </td>
                <td style="padding: 1rem;">
                    <div>${u.business.business_name || '-'}</div>
                </td>
                <td style="padding: 1rem; font-family: monospace; font-size: 0.8rem;">
                    ${u.parent_reseller_id.substring(0, 8)}...
                </td>
                 <td style="padding: 1rem;">
                    <span class="badge ${u.whatsapp_mode === 'official' ? 'badge-success' : 'badge-warning'}">
                        ${u.whatsapp_mode}
                    </span>
                </td>
                <td style="padding: 1rem;">
                    ${u.wallet?.credits_allocated || 0} / ${u.wallet?.credits_used || 0}
                </td>
                <td style="padding: 1rem;">
                    <span class="badge ${u.status === 'active' ? 'badge-success' : 'badge-gray'}">
                        ${u.status}
                    </span>
                </td>
            </tr>
        `).join('');

    } catch (error) {
        console.error('Error loading business users:', error);
        tbody.innerHTML = '<tr><td colspan="6" style="padding: 1rem; text-align: center; color: red;">Error loading data.</td></tr>';
    }
}
