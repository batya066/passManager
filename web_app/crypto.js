// Web Crypto API kullanarak encryption/decryption
// Python'daki crypto.py mantığını JavaScript'e uyarladık

const SALT_SIZE = 16;
const NONCE_SIZE = 12;
const KDF_ITERATIONS = 310000;

// Base64 encoding/decoding (standard base64, Python ile uyumlu)
function b64encode(data) {
    const bytes = new Uint8Array(data);
    let binary = '';
    for (let i = 0; i < bytes.length; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
}

function b64decode(str) {
    const binary = atob(str);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }
    return bytes;
}

// PBKDF2 key derivation
async function deriveKey(password, salt, iterations = KDF_ITERATIONS) {
    const encoder = new TextEncoder();
    const passwordKey = await crypto.subtle.importKey(
        'raw',
        encoder.encode(password),
        'PBKDF2',
        false,
        ['deriveBits']
    );
    
    const keyMaterial = await crypto.subtle.deriveBits(
        {
            name: 'PBKDF2',
            salt: salt,
            iterations: iterations,
            hash: 'SHA-512'
        },
        passwordKey,
        256 // 32 bytes = 256 bits
    );
    
    return await crypto.subtle.importKey(
        'raw',
        keyMaterial,
        { name: 'AES-GCM' },
        false,
        ['encrypt', 'decrypt']
    );
}

// SHA-256 hash (Python ile uyumlu)
async function sha3_256(data) {
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

// Encrypt payload
async function encryptPayload(masterPassword, payload) {
    // Generate salt and nonce
    const salt = crypto.getRandomValues(new Uint8Array(SALT_SIZE));
    const nonce = crypto.getRandomValues(new Uint8Array(NONCE_SIZE));
    
    // Derive key
    const key = await deriveKey(masterPassword, salt);
    
    // Serialize payload
    const serialized = new TextEncoder().encode(JSON.stringify(payload));
    
    // Encrypt
    const ciphertext = await crypto.subtle.encrypt(
        {
            name: 'AES-GCM',
            iv: nonce
        },
        key,
        serialized
    );
    
    // Calculate checksum
    const checksum = await sha3_256(new Uint8Array(ciphertext));
    
    return {
        version: 1,
        kdf: {
            name: 'PBKDF2-HMAC-SHA512',
            iterations: KDF_ITERATIONS,
            salt: b64encode(salt)
        },
        cipher: {
            name: 'AES-256-GCM',
            nonce: b64encode(nonce),
            payload: b64encode(ciphertext)
        },
        checksum: checksum
    };
}

// Decrypt payload
async function decryptPayload(masterPassword, envelope) {
    try {
        const kdf = envelope.kdf;
        const cipher = envelope.cipher;
        
        const salt = b64decode(kdf.salt);
        const iterations = parseInt(kdf.iterations);
        const nonce = b64decode(cipher.nonce);
        const ciphertext = b64decode(cipher.payload);
        const checksum = envelope.checksum;
        
        // Verify checksum
        const calculatedChecksum = await sha3_256(ciphertext);
        if (checksum !== calculatedChecksum) {
            throw new Error('Kasa bütünlük doğrulamasından geçemedi.');
        }
        
        // Derive key
        const key = await deriveKey(masterPassword, salt, iterations);
        
        // Decrypt
        const plaintext = await crypto.subtle.decrypt(
            {
                name: 'AES-GCM',
                iv: nonce
            },
            key,
            ciphertext
        );
        
        // Parse JSON
        const decoded = new TextDecoder().decode(plaintext);
        return JSON.parse(decoded);
    } catch (error) {
        if (error.message.includes('bütünlük')) {
            throw error;
        }
        throw new Error('Ana parola hatalı veya veri bozulmuş.');
    }
}

// Export functions
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { encryptPayload, decryptPayload };
}

