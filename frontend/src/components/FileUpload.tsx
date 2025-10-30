'use client';

import { Group, Text, rem } from '@mantine/core';
import { Dropzone, MIME_TYPES } from '@mantine/dropzone';
import { IconCloudUpload, IconX, IconDownload } from '@tabler/icons-react';
import { useState } from 'react';
import axios from 'axios';
import { notifications } from '@mantine/notifications';
import { useAuthStore } from '../store/auth';
import * as crypto from '../lib/crypto';

const API_URL = 'http://localhost:8000';
const CHUNK_SIZE = 4 * 1024 * 1024; // 4MB

export function FileUpload() {
  const token = useAuthStore((state) => state.token);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleDrop = async (files: File[]) => {
    if (!token) {
        notifications.show({
            title: 'Authentication Error',
            message: 'You must be logged in to upload files.',
            color: 'red',
        });
        return;
    }

    setUploading(true);
    const file = files[0];

    try {
        // 1. Generate a new Data Encryption Key (DEK) for this file
        const dek = await crypto.generateDEK();

        const password = prompt('Please enter your password to encrypt the file:');
        if (!password) {
            notifications.show({ title: 'Password required', message: 'Password is required to encrypt and upload the file.', color: 'red' });
            setUploading(false);
            return;
        }

        // 1. Get user's salt to derive KEK
        const saltResponse = await axios.get(`${API_URL}/auth/salt`, {
            headers: { Authorization: `Bearer ${token}` },
        });
        const salt = Buffer.from(saltResponse.data.salt, 'base64');

        // 2. Derive the Key Encryption Key (KEK) from the user's password
        const kek = await crypto.getKEK(password, salt);

        // 3. Wrap the DEK with the KEK
        const wrappedDek = await crypto.wrapDEK(dek, kek);

        // 4. Encrypt the filename
        const encryptedFilename = await crypto.encryptChunk(new TextEncoder().encode(file.name), dek);

        // 5. Initialize the upload with the backend
        const response = await axios.post(
            `${API_URL}/files/upload/init`,
            {
                original_filename_encrypted: Buffer.from(encryptedFilename).toString('base64'),
                size_bytes: file.size,
                mime_type: file.type,
                wrapped_dek: Buffer.from(wrappedDek).toString('base64'),
            },
            {
                headers: { Authorization: `Bearer ${token}` },
            }
        );

        const { id: fileId } = response.data;

        // 6. Upload the file in chunks
        let offset = 0;
        while (offset < file.size) {
            const chunk = file.slice(offset, offset + CHUNK_SIZE);
            const encryptedChunk = await crypto.encryptChunk(await chunk.arrayBuffer(), dek);

            const formData = new FormData();
            formData.append('chunk', new Blob([encryptedChunk]));

            await axios.post(`${API_URL}/files/upload/${fileId}/chunk`, formData, {
                headers: { Authorization: `Bearer ${token}` },
            });

            offset += CHUNK_SIZE;
            setProgress(Math.min(Math.round((offset / file.size) * 100), 100));
        }

        // 7. Finalize the upload
        await axios.post(`${API_URL}/files/upload/${fileId}/complete`, {}, {
            headers: { Authorization: `Bearer ${token}` },
        });

        notifications.show({
            title: 'Upload Complete',
            message: `${file.name} has been securely uploaded.`,
            color: 'green',
        });

    } catch (error: any) {
        notifications.show({
            title: 'Upload Failed',
            message: error.response?.data?.detail || 'An unexpected error occurred.',
            color: 'red',
        });
    } finally {
        setUploading(false);
        setProgress(0);
    }
  };

  return (
    <Dropzone
      onDrop={handleDrop}
      onReject={(files) => console.log('rejected files', files)}
      maxSize={50 * 1024 ** 2}
      accept={[MIME_TYPES.pdf, MIME_TYPES.docx, MIME_TYPES.xlsx, MIME_TYPES.csv]}
      loading={uploading}
      style={{ minHeight: rem(220), pointerEvents: uploading ? 'none' : 'all' }}
    >
      <Group justify="center" gap="xl" style={{ minHeight: rem(220) }}>
        <Dropzone.Accept>
          <IconDownload
            style={{ width: rem(52), height: rem(52), color: 'var(--mantine-color-blue-6)' }}
            stroke={1.5}
          />
        </Dropzone.Accept>
        <Dropzone.Reject>
          <IconX
            style={{ width: rem(52), height: rem(52), color: 'var(--mantine-color-red-6)' }}
            stroke={1.5}
          />
        </Dropzone.Reject>
        <Dropzone.Idle>
          <IconCloudUpload
            style={{ width: rem(52), height: rem(52), color: 'var(--mantine-color-dimmed)' }}
            stroke={1.5}
          />
        </Dropzone.Idle>

        <div>
          <Text size="xl" inline>
            Drag files here or click to select files
          </Text>
          <Text size="sm" c="dimmed" inline mt={7}>
            Attach as many files as you like, each file should not exceed 50mb
          </Text>
        </div>
      </Group>
    </Dropzone>
  );
}