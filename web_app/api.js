// API client
class PassManagerAPI {
    constructor(baseURL) {
        this.baseURL = baseURL.replace(/\/$/, '');
        this.token = localStorage.getItem('pm_token');
        this.username = localStorage.getItem('pm_username');
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: 'Bir hata oluştu' }));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            throw error;
        }
    }

    async register(username, password) {
        const data = await this.request('/api/v1/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        this.token = data.token;
        this.username = data.username;
        localStorage.setItem('pm_token', this.token);
        localStorage.setItem('pm_username', this.username);
        return data;
    }

    async login(username, password) {
        const data = await this.request('/api/v1/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        this.token = data.token;
        this.username = data.username;
        localStorage.setItem('pm_token', this.token);
        localStorage.setItem('pm_username', this.username);
        return data;
    }

    async getVault() {
        return await this.request('/api/v1/vault');
    }

    async saveVault(encryptedEnvelope) {
        return await this.request('/api/v1/vault', {
            method: 'POST',
            body: JSON.stringify({ encrypted_envelope: encryptedEnvelope })
        });
    }

    logout() {
        this.token = null;
        this.username = null;
        localStorage.removeItem('pm_token');
        localStorage.removeItem('pm_username');
        localStorage.removeItem('pm_vault');
    }

    isAuthenticated() {
        return !!this.token;
    }
}

