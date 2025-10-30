'use client';

import { Container, Title, Paper, Text, Progress } from '@mantine/core';
import { FileUpload } from '../../components/FileUpload';
import { FileList } from '../../components/FileList';
import { useAuthStore } from '../../store/auth';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function DashboardPage() {
  const token = useAuthStore((state) => state.token);
  const router = useRouter();

  useEffect(() => {
    if (!token) {
      router.replace('/');
    }
  }, [token, router]);

  if (!token) {
    return null; // or a loading spinner
  }

  return (
    <Container my="lg">
      <Title order={2} mb="lg">
        My Files
      </Title>

      <Paper withBorder p="lg" radius="md" mb="xl">
        <Text size="lg" fw={500}>Storage Usage</Text>
        <Progress value={50} mt="md" size="lg" radius="xl" />
        <Text c="dimmed" size="sm" mt="xs">5 GB / 10 GB used</Text>
      </Paper>

      <FileUpload />

      <Title order={3} mt="xl" mb="md">
        All Files
      </Title>
      <FileList />
    </Container>
  );
}