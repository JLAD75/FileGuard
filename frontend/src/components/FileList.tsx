'use client';

import { useEffect, useState } from 'react';
import { Table, Text, Anchor } from '@mantine/core';
import axios from 'axios';
import { useAuthStore } from '../store/auth';
import * as crypto from '../lib/crypto';
import { notifications } from '@mantine/notifications';

const API_URL = 'http://localhost:8000';

interface FileMetadata {
    id: string;
    original_filename_encrypted: string;
    size_bytes: number;
    mime_type: string;
    updated_at: string;
    wrapped_dek: string;
}

export function FileList() {
    const token = useAuthStore((state) => state.token);
    const [files, setFiles] = useState<FileMetadata[]>([]);

    useEffect(() => {
        const fetchFiles = async () => {
            if (!token) return;

            try {
                const response = await axios.get(`${API_URL}/files/`, {
                    headers: { Authorization: `Bearer ${token}` },
                });
                setFiles(response.data);
            } catch (error) {
                notifications.show({
                    title: 'Failed to fetch files',
                    message: 'Could not retrieve your file list.',
                    color: 'red',
                });
            }
        };

        fetchFiles();
    }, [token]);

  const handleDownload = async (file: FileMetadata) => {
    if (!token) return;

    const password = prompt('Please enter your password to decrypt the file:');
    if (!password) {
        notifications.show({ title: 'Password required', message: 'Password is required to decrypt and download the file.', color: 'red' });
        return;
    }

    try {
        // 1. Get user's salt to derive KEK
        const saltResponse = await axios.get(`${API_URL}/auth/salt`, {
            headers: { Authorization: `Bearer ${token}` },
        });
        const salt = Buffer.from(saltResponse.data.salt, 'base64');

        // 2. Re-derive KEK from password
        const kek = await crypto.getKEK(password, salt);

        // 3. Fetch the file metadata to get the wrapped DEK
        const wrappedDek = Buffer.from(file.wrapped_dek, 'base64');

        // 3. Unwrap the DEK
        const dek = await crypto.unwrapDEK(wrappedDek, kek);

        // 4. Decrypt the filename
        const encryptedFilenameBytes = Buffer.from(file.original_filename_encrypted, 'base64');
        const decryptedFilenameBytes = await crypto.decryptChunk(encryptedFilenameBytes, dek);
        const decryptedFilename = new TextDecoder().decode(decryptedFilenameBytes);

        // 5. Download the encrypted file content
        const response = await axios.get(`${API_URL}/files/download/${file.id}`, {
            headers: { Authorization: `Bearer ${token}` },
            responseType: 'arraybuffer',
        });

        // 6. Decrypt the content
        const decryptedContent = await crypto.decryptChunk(response.data, dek);

        // 7. Trigger browser download
        const blob = new Blob([decryptedContent], { type: file.mime_type });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = decryptedFilename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();

    } catch (error) {
        notifications.show({
            title: 'Download Failed',
            message: 'Could not decrypt or download the file. Please check your password.',
            color: 'red',
        });
    }
  };

    const rows = files.map((file) => (
        <Table.Tr key={file.id}>
            <Table.Td>
                <Anchor component="button" size="sm" onClick={() => handleDownload(file)}>
                    {`[Encrypted] ${file.id.substring(0, 8)}...`}
                </Anchor>
            </Table.Td>
            <Table.Td>{(file.size_bytes / 1024 / 1024).toFixed(2)} MB</Table.Td>
            <Table.Td>{file.mime_type}</Table.Td>
            <Table.Td>{new Date(file.updated_at).toLocaleDateString()}</Table.Td>
        </Table.Tr>
    ));

    return (
        <Table>
            <Table.Thead>
                <Table.Tr>
                    <Table.Th>Name</Table.Th>
                    <Table.Th>Size</Table.Th>
                    <Table.Th>Type</Table.Th>
                    <Table.Th>Last Modified</Table.Th>
                </Table.Tr>
            </Table.Thead>
            <Table.Tbody>{rows}</Table.Tbody>
        </Table>
    );
}