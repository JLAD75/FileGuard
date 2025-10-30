// IMPORTANT: This is a placeholder for a proper Argon2 implementation.
// In a real application, use a library like 'argon2-browser'.
async function deriveKeyFromPassword(password: string, salt: Uint8Array): Promise<CryptoKey> {
    const enc = new TextEncoder();
    const keyMaterial = await window.crypto.subtle.importKey(
        'raw',
        enc.encode(password),
        { name: 'PBKDF2' },
        false,
        ['deriveKey']
    );
    return window.crypto.subtle.deriveKey(
        {
            name: 'PBKDF2',
            salt: salt,
            iterations: 100000,
            hash: 'SHA-256',
        },
        keyMaterial,
        { name: 'AES-GCM', length: 256 },
        true,
        ['wrapKey', 'unwrapKey']
    );
}

export async function getKEK(password: string, salt: string): Promise<CryptoKey> {
    const saltBytes = new TextEncoder().encode(salt);
    return deriveKeyFromPassword(password, saltBytes);
}

export async function generateDEK(): Promise<CryptoKey> {
    return window.crypto.subtle.generateKey(
        {
            name: 'AES-GCM',
            length: 256,
        },
        true,
        ['encrypt', 'decrypt']
    );
}

export async function wrapDEK(dek: CryptoKey, kek: CryptoKey): Promise<ArrayBuffer> {
    return window.crypto.subtle.wrapKey('raw', dek, kek, 'AES-GCM');
}

export async function unwrapDEK(wrappedDek: ArrayBuffer, kek: CryptoKey): Promise<CryptoKey> {
    return window.crypto.subtle.unwrapKey(
        'raw',
        wrappedDek,
        kek,
        'AES-GCM',
        { name: 'AES-GCM', length: 256 },
        true,
        ['encrypt', 'decrypt']
    );
}

export async function encryptChunk(chunk: ArrayBuffer, dek: CryptoKey): Promise<ArrayBuffer> {
    const iv = window.crypto.getRandomValues(new Uint8Array(12));
    const encryptedChunk = await window.crypto.subtle.encrypt(
        {
            name: 'AES-GCM',
            iv: iv,
        },
        dek,
        chunk
    );

    // Prepend IV to the encrypted chunk for decryption
    const result = new Uint8Array(iv.length + encryptedChunk.byteLength);
    result.set(iv, 0);
    result.set(new Uint8Array(encryptedChunk), iv.length);

    return result.buffer;
}

export async function decryptChunk(encryptedChunkWithIv: ArrayBuffer, dek: CryptoKey): Promise<ArrayBuffer> {
    const iv = encryptedChunkWithIv.slice(0, 12);
    const encryptedChunk = encryptedChunkWithIv.slice(12);

    return window.crypto.subtle.decrypt(
        {
            name: 'AES-GCM',
            iv: new Uint8Array(iv),
        },
        dek,
        encryptedChunk
    );
}