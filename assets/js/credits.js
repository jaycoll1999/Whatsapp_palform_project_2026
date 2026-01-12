const API_BASE = 'http://localhost:8000';

// Store data globally to avoid re-fetching constantly
let allResellers = [];
let allBusinessUsers = [];

window.addEventListener('page-loaded', (e) => {
    if (e.detail.page === 'credits') {
        initCreditsPage();
    }
});

function initCreditsPage() {
    console.log('Credits Page Initialized');

    // Initial Load
    fetchDataAndInitialize();
    loadCreditHistory();
    loadUsageLogs();

    const form = document.getElementById('credit-distribution-form');
    if (form) {
        form.removeEventListener('submit', handleDistributeCredits);
        form.addEventListener('submit', handleDistributeCredits);
    }
}

async function fetchDataAndInitialize() {
    try {
        const [resResellers, resUsers] = await Promise.all([
            fetch(`${API_BASE}/resellers`),
            fetch(`${API_BASE}/business-users`)
        ]);

        if (resResellers.ok) allResellers = await resResellers.json();
        if (resUsers.ok) allBusinessUsers = await resUsers.json();

        populateResellerDropdown();

    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

function populateResellerDropdown() {
    const select = document.getElementById('reseller-select');
    if (!select) return;

    if (allResellers.length === 0) {
        select.innerHTML = '<option value="">No Resellers Found</option>';
        return;
    }

    select.innerHTML = '<option value="">Select Reseller</option>' +
        allResellers.map(r => `<option value="${r.user_id}">${r.profile.name} (Bal: ${r.wallet?.available_credits || 0})</option>`).join('');
}

// Global function called by onchange in HTML
window.filterBusinessUsers = function (resellerId) {
    const userSelect = document.getElementById('business-user-select');
    const balanceText = document.getElementById('reseller-balance');

    if (!resellerId) {
        userSelect.innerHTML = '<option value="">Select Reseller First</option>';
        userSelect.disabled = true;
        balanceText.textContent = '';
        return;
    }

    // Update Balance Text
    const reseller = allResellers.find(r => r.user_id === resellerId);
    if (reseller) {
        balanceText.textContent = `Available Balance: ${reseller.wallet?.available_credits || 0}`;
    }

    // Filter Users
    const filteredUsers = allBusinessUsers.filter(u => u.parent_reseller_id === resellerId);

    if (filteredUsers.length === 0) {
        userSelect.innerHTML = '<option value="">No Business Users for this Reseller</option>';
        userSelect.disabled = true;
    } else {
        userSelect.innerHTML = '<option value="">Select Business User</option>' +
            filteredUsers.map(u => `<option value="${u.user_id}">${u.profile.name}</option>`).join('');
        userSelect.disabled = false;
    }
};

async function handleDistributeCredits(e) {
    e.preventDefault();
    const form = e.target;
    const btn = form.querySelector('button[type="submit"]');
    const originalText = btn.textContent;
    btn.textContent = 'Processing...';
    btn.disabled = true;

    const formData = new FormData(form);
    const payload = {
        from_reseller_id: formData.get('from_reseller_id'),
        to_business_user_id: formData.get('to_business_user_id'),
        credits: parseFloat(formData.get('credits'))
    };

    try {
        const response = await fetch(`${API_BASE}/credits/distribute`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const err = await response.json();
            alert(`Error: ${err.detail || 'Failed to distribute credits'}`);
            return;
        }

        alert('Credits distributed successfully!');
        form.reset();

        // Refresh data to update balances
        await fetchDataAndInitialize();

        // Reset specific UI elements
        document.getElementById('business-user-select').disabled = true;
        document.getElementById('reseller-balance').textContent = '';

        loadCreditHistory();

    } catch (error) {
        console.error('Error distributing credits:', error);
        alert('Network error occurred.');
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

async function loadCreditHistory() {
    const tbody = document.getElementById('credit-history-table-body');
    if (!tbody) return;

    tbody.innerHTML = '<tr><td colspan="4" style="padding: 1rem; text-align: center;">Loading...</td></tr>';

    try {
        const response = await fetch(`${API_BASE}/credits/history`);
        if (!response.ok) throw new Error('Failed to fetch history');

        const history = await response.json();

        if (history.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="padding: 1rem; text-align: center;">No transactions found.</td></tr>';
            return;
        }

        tbody.innerHTML = history.map(t => {
            // Mapping IDs to Names (Best effort with loaded data)
            const reseller = allResellers.find(r => r.user_id === t.from_reseller_id);
            const user = allBusinessUsers.find(u => u.user_id === t.to_business_user_id);

            return `
            <tr>
                <td style="padding: 1rem;">
                    ${new Date(t.shared_at).toLocaleString()}
                </td>
                <td style="padding: 1rem;">
                    ${reseller ? reseller.profile.name : t.from_reseller_id.substring(0, 8) + '...'}
                </td>
                <td style="padding: 1rem;">
                     ${user ? user.profile.name : t.to_business_user_id.substring(0, 8) + '...'}
                </td>
                <td style="padding: 1rem; font-weight: bold; color: var(--success, green);">
                    +${t.credits_shared}
                </td>
            </tr>
        `;
        }).join('');

    } catch (error) {
        console.error('Error loading history:', error);
        tbody.innerHTML = '<tr><td colspan="4" style="padding: 1rem; text-align: center; color: red;">Error loading data.</td></tr>';
    }
}

window.loadUsageLogs = async function () {
    const tbody = document.getElementById('usage-logs-table-body');
    if (!tbody) return;

    tbody.innerHTML = '<tr><td colspan="5" style="padding: 1rem; text-align: center;">Loading...</td></tr>';

    // Simple date filter logic (client-side or server-side supported?)
    // Our backend route currently only supports user_id, skip, limit.
    // We will just fetch all logs for now. To support date filtering, we would need to update backend.

    try {
        const response = await fetch(`${API_BASE}/usage/logs`);
        if (!response.ok) throw new Error('Failed to fetch logs');

        let logs = await response.json();

        // Client-side date filtering if needed
        const dateFilter = document.getElementById('log-date-filter')?.value;
        if (dateFilter) {
            logs = logs.filter(l => l.timestamp.startsWith(dateFilter));
        }

        if (logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="padding: 1rem; text-align: center;">No usage logs found.</td></tr>';
            return;
        }

        tbody.innerHTML = logs.map(l => {
            const user = allBusinessUsers.find(u => u.user_id === l.user_id);
            return `
            <tr>
                <td style="padding: 1rem; font-size: 0.85rem;">
                    ${new Date(l.timestamp).toLocaleString()}
                </td>
                <td style="padding: 1rem;">
                    ${user ? user.profile.name : l.user_id.substring(0, 8) + '...'}
                </td>
                <td style="padding: 1rem;">
                     Message Sent
                </td>
                <td style="padding: 1rem; color: var(--danger, red); font-weight: bold;">
                    -${l.credits_deducted}
                </td>
                <td style="padding: 1rem; font-family: monospace;">
                    ${l.balance_after.toFixed(2)}
                </td>
            </tr>
            `;
        }).join('');

    } catch (error) {
        console.error('Error loading logs:', error);
        tbody.innerHTML = '<tr><td colspan="5" style="padding: 1rem; text-align: center; color: red;">Error loading logs.</td></tr>';
    }
};
