// Main application logic
let api = null;
let vault = null;
let masterPassword = null;
let currentEntryId = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeAuth();
    setupEventListeners();
    
    // Check if already authenticated
    const token = localStorage.getItem('pm_token');
    if (token) {
        // API URL'ini otomatik algıla (aynı domain)
        const currentOrigin = window.location.origin;
        const apiUrl = localStorage.getItem('pm_api_url') || currentOrigin;
        api = new PassManagerAPI(apiUrl);
        showAppScreen();
    }
    
    // API URL'ini otomatik doldur
    const currentOrigin = window.location.origin;
    document.getElementById('login-api-url').value = currentOrigin;
    document.getElementById('register-api-url').value = currentOrigin;
});

function initializeAuth() {
    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(`${tab}-form`).classList.add('active');
        });
    });

    // Login form
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;
        const apiUrl = document.getElementById('login-api-url').value;

        try {
            api = new PassManagerAPI(apiUrl);
            await api.login(username, password);
            localStorage.setItem('pm_api_url', apiUrl);
            showAppScreen();
        } catch (error) {
            showError('auth-error', error.message);
        }
    });

    // Register form
    document.getElementById('register-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('register-username').value;
        const password = document.getElementById('register-password').value;
        const apiUrl = document.getElementById('register-api-url').value;

        if (password.length < 8) {
            showError('register-error', 'Parola en az 8 karakter olmalı');
            return;
        }

        try {
            api = new PassManagerAPI(apiUrl);
            await api.register(username, password);
            localStorage.setItem('pm_api_url', apiUrl);
            showAppScreen();
        } catch (error) {
            showError('register-error', error.message);
        }
    });
}

function setupEventListeners() {
    // Logout
    document.getElementById('logout-btn').addEventListener('click', () => {
        if (api) api.logout();
        showAuthScreen();
    });

    // Unlock vault
    document.getElementById('unlock-btn').addEventListener('click', unlockVault);
    document.getElementById('master-password-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') unlockVault();
    });

    // Sync
    document.getElementById('sync-btn').addEventListener('click', syncVault);

    // Add entry
    document.getElementById('add-entry-btn').addEventListener('click', () => {
        currentEntryId = null;
        document.getElementById('modal-title').textContent = 'Yeni Kayıt';
        document.getElementById('entry-form').reset();
        document.getElementById('entry-modal').classList.remove('hidden');
    });

    // Generate password
    document.getElementById('generate-password-btn').addEventListener('click', generatePassword);

    // Entry form
    document.getElementById('entry-form').addEventListener('submit', saveEntry);

    // Cancel
    document.getElementById('cancel-btn').addEventListener('click', () => {
        document.getElementById('entry-modal').classList.add('hidden');
    });

    // Search
    document.getElementById('search-input').addEventListener('input', (e) => {
        filterEntries(e.target.value);
    });

    // Close detail
    document.getElementById('close-detail-btn').addEventListener('click', () => {
        document.getElementById('detail-modal').classList.add('hidden');
    });

    // Reveal password
    document.getElementById('reveal-password-btn').addEventListener('click', () => {
        const span = document.getElementById('detail-password');
        if (span.classList.contains('password-hidden')) {
            const entry = vault.entries.find(e => e.entry_id === currentEntryId);
            span.textContent = entry.password;
            span.classList.remove('password-hidden');
        } else {
            span.textContent = '●●●●●●●●●●●●';
            span.classList.add('password-hidden');
        }
    });

    // Copy password
    document.getElementById('copy-password-btn').addEventListener('click', () => {
        const entry = vault.entries.find(e => e.entry_id === currentEntryId);
        navigator.clipboard.writeText(entry.password);
        alert('Parola kopyalandı!');
    });

    // Delete entry
    document.getElementById('delete-entry-btn').addEventListener('click', deleteEntry);
}

function showAuthScreen() {
    document.getElementById('auth-screen').classList.add('active');
    document.getElementById('app-screen').classList.remove('active');
}

function showAppScreen() {
    document.getElementById('auth-screen').classList.remove('active');
    document.getElementById('app-screen').classList.add('active');
    document.getElementById('master-password-prompt').classList.remove('hidden');
    document.getElementById('vault-content').classList.add('hidden');
}

function showError(elementId, message) {
    const errorEl = document.getElementById(elementId);
    errorEl.textContent = message;
    errorEl.classList.add('show');
    setTimeout(() => errorEl.classList.remove('show'), 5000);
}

async function unlockVault() {
    masterPassword = document.getElementById('master-password-input').value;
    if (!masterPassword) {
        showError('master-password-error', 'Ana parola gerekli');
        return;
    }

    try {
        await loadVault();
        document.getElementById('master-password-prompt').classList.add('hidden');
        document.getElementById('vault-content').classList.remove('hidden');
        renderEntries();
    } catch (error) {
        showError('master-password-error', error.message);
    }
}

async function loadVault() {
    try {
        const response = await api.getVault();
        const envelope = response.encrypted_envelope;
        
        if (!envelope || Object.keys(envelope).length === 0) {
            // Empty vault
            vault = { entries: [], meta: { created_at: new Date().toISOString() } };
            return;
        }

        const decrypted = await decryptPayload(masterPassword, envelope);
        vault = {
            entries: decrypted.entries || [],
            meta: decrypted.meta || {}
        };
    } catch (error) {
        throw new Error('Ana parola hatalı veya veri bozulmuş.');
    }
}

async function saveVault() {
    const envelope = await encryptPayload(masterPassword, {
        entries: vault.entries,
        meta: vault.meta
    });
    await api.saveVault(envelope);
}

async function syncVault() {
    try {
        await loadVault();
        renderEntries();
        alert('Vault senkronize edildi!');
    } catch (error) {
        alert('Senkronizasyon hatası: ' + error.message);
    }
}

function renderEntries(filter = '') {
    const container = document.getElementById('entries-list');
    let entries = vault.entries || [];

    if (filter) {
        const lowerFilter = filter.toLowerCase();
        entries = entries.filter(entry => {
            const haystack = `${entry.service}|${entry.username}|${entry.tags.join(' ')}`.toLowerCase();
            return haystack.includes(lowerFilter);
        });
    }

    if (entries.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-light);">Kayıt bulunamadı.</p>';
        return;
    }

    container.innerHTML = entries.map(entry => `
        <div class="entry-card" data-id="${entry.entry_id}">
            <div class="entry-header">
                <div>
                    <div class="entry-service">${escapeHtml(entry.service)}</div>
                    <div class="entry-id">${entry.entry_id}</div>
                </div>
            </div>
            <div class="entry-username">👤 ${escapeHtml(entry.username)}</div>
            ${entry.tags && entry.tags.length > 0 ? `
                <div class="entry-tags">
                    ${entry.tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
                </div>
            ` : ''}
        </div>
    `).join('');

    // Add click listeners
    container.querySelectorAll('.entry-card').forEach(card => {
        card.addEventListener('click', () => {
            const id = card.dataset.id;
            showEntryDetail(id);
        });
    });
}

function filterEntries(query) {
    renderEntries(query);
}

function showEntryDetail(entryId) {
    currentEntryId = entryId;
    const entry = vault.entries.find(e => e.entry_id === entryId);
    if (!entry) return;

    document.getElementById('detail-service').textContent = entry.service;
    document.getElementById('detail-username').textContent = entry.username;
    document.getElementById('detail-password').textContent = '●●●●●●●●●●●●';
    document.getElementById('detail-password').classList.add('password-hidden');
    document.getElementById('detail-tags').textContent = entry.tags && entry.tags.length > 0 
        ? entry.tags.join(', ') : '-';
    document.getElementById('detail-notes').textContent = entry.notes || '-';
    document.getElementById('detail-created').textContent = entry.created_at || '-';
    
    document.getElementById('detail-modal').classList.remove('hidden');
}

async function saveEntry(e) {
    e.preventDefault();
    
    const service = document.getElementById('entry-service').value;
    const username = document.getElementById('entry-username').value;
    const password = document.getElementById('entry-password').value;
    const tagsStr = document.getElementById('entry-tags').value;
    const notes = document.getElementById('entry-notes').value;

    const tags = tagsStr.split(',').map(t => t.trim()).filter(t => t);

    if (currentEntryId) {
        // Update existing
        const entry = vault.entries.find(e => e.entry_id === currentEntryId);
        entry.service = service;
        entry.username = username;
        entry.password = password;
        entry.tags = tags;
        entry.notes = notes;
        entry.updated_at = new Date().toISOString();
    } else {
        // Add new
        const entry = {
            entry_id: generateId(),
            service,
            username,
            password,
            tags,
            notes,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
        };
        vault.entries.push(entry);
    }

    await saveVault();
    document.getElementById('entry-modal').classList.add('hidden');
    renderEntries();
}

async function deleteEntry() {
    if (!confirm('Bu kaydı silmek istediğinize emin misiniz?')) return;

    vault.entries = vault.entries.filter(e => e.entry_id !== currentEntryId);
    await saveVault();
    document.getElementById('detail-modal').classList.add('hidden');
    renderEntries();
}

function generatePassword() {
    const length = 24;
    const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';
    let password = '';
    const array = new Uint8Array(length);
    crypto.getRandomValues(array);
    for (let i = 0; i < length; i++) {
        password += charset[array[i] % charset.length];
    }
    document.getElementById('entry-password').value = password;
    document.getElementById('entry-password').type = 'text';
    setTimeout(() => {
        document.getElementById('entry-password').type = 'password';
    }, 2000);
}

function generateId() {
    return Array.from(crypto.getRandomValues(new Uint8Array(12)))
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

