const API_BASE = 'http://localhost:8000';

let allBusinessUsers = [];

window.addEventListener('page-loaded', (e) => {
    if (e.detail.page === 'send-message') {
        initSendMessagePage();
    }
});

function initSendMessagePage() {
    console.log('Send Message Page Initialized');

    // Initial Load
    fetchUsersAndInitialize();
    loadMessageHistory();

    const form = document.getElementById('send-message-form');
    if (form) {
        form.removeEventListener('submit', handleSendMessage);
        form.addEventListener('submit', handleSendMessage);
    }
}

async function fetchUsersAndInitialize() {
    try {
        const response = await fetch(`${API_BASE}/business-users`);
        if (response.ok) {
            allBusinessUsers = await response.json();
            populateSenderDropdown();
        }
    } catch (error) {
        console.error('Error fetching users:', error);
    }
}

function populateSenderDropdown() {
    const select = document.getElementById('sender-select');
    if (!select) return;

    if (allBusinessUsers.length === 0) {
        select.innerHTML = '<option value="">No Users Found</option>';
        return;
    }

    select.innerHTML = '<option value="">Select Sender</option>' +
        allBusinessUsers.map(u => `<option value="${u.user_id}">${u.profile.name} (${u.business.business_name})</option>`).join('');
}

window.updateSenderInfo = function (userId) {
    const info = document.getElementById('sender-info');
    const user = allBusinessUsers.find(u => u.user_id === userId);

    if (user) {
        info.innerHTML = `Available Credits: <b>${user.wallet?.credits_remaining || 0}</b> | Mode: ${user.whatsapp_mode}`;
        // Auto-select mode based on user preference if desired
        const modeSelect = document.getElementById('mode-select');
        if (modeSelect) modeSelect.value = user.whatsapp_mode || 'official';
    } else {
        info.textContent = '';
    }
};

async function handleSendMessage(e) {
    e.preventDefault();
    const form = e.target;
    const btn = form.querySelector('button[type="submit"]');
    const originalText = btn.textContent;
    btn.textContent = 'Sending...';
    btn.disabled = true;

    const formData = new FormData(form);
    const payload = {
        user_id: formData.get('user_id'),
        mode: formData.get('mode'),
        sender_number: formData.get('sender_number'),
        receiver_number: formData.get('receiver_number'),
        message_body: formData.get('message_body'),
        message_type: 'text'
    };

    try {
        const response = await fetch(`${API_BASE}/messages/send`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const err = await response.json();
            alert(`Error: ${err.detail || 'Failed to send message'}`);
            return;
        }

        alert('Message sent successfully!');
        form.reset();
        loadMessageHistory();

        // Refresh users to show updated balance
        await fetchUsersAndInitialize();

        // Clear info
        document.getElementById('sender-info').textContent = '';

    } catch (error) {
        console.error('Error sending message:', error);
        alert('Network error occurred.');
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

async function loadMessageHistory() {
    const tbody = document.getElementById('message-history-table-body');
    if (!tbody) return;

    tbody.innerHTML = '<tr><td colspan="6" style="padding: 1rem; text-align: center;">Loading...</td></tr>';

    try {
        const response = await fetch(`${API_BASE}/messages`);
        if (!response.ok) throw new Error('Failed to fetch messages');

        const messages = await response.json();

        if (messages.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="padding: 1rem; text-align: center;">No messages sent yet.</td></tr>';
            return;
        }

        tbody.innerHTML = messages.map(m => {
            const sender = allBusinessUsers.find(u => u.user_id === m.user_id);
            return `
            <tr>
                <td style="padding: 1rem;">
                    ${new Date(m.sent_at).toLocaleString()}
                </td>
                <td style="padding: 1rem;">
                    ${sender ? sender.profile.name : m.user_id.substring(0, 8) + '...'}
                </td>
                <td style="padding: 1rem;">
                     ${m.receiver_number}
                </td>
                <td style="padding: 1rem;">
                    <span class="badge ${m.mode === 'official' ? 'badge-success' : 'badge-warning'}">${m.mode}</span>
                </td>
                <td style="padding: 1rem;">
                    <span class="badge badge-gray">${m.status}</span>
                </td>
                <td style="padding: 1rem;">
                    ${m.credits_used}
                </td>
            </tr>
        `;
        }).join('');

    } catch (error) {
        console.error('Error loading messages:', error);
        tbody.innerHTML = '<tr><td colspan="6" style="padding: 1rem; text-align: center; color: red;">Error loading history.</td></tr>';
    }
}
