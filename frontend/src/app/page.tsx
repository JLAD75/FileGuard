'use client';

import {
  TextInput,
  PasswordInput,
  Checkbox,
  Anchor,
  Paper,
  Title,
  Text,
  Container,
  Group,
  Button,
  Tabs,
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { useState } from 'react';
import axios from 'axios';
import { notifications } from '@mantine/notifications';
import { useAuthStore } from '../store/auth';
import { useRouter } from 'next/navigation';
import * as crypto from '../lib/crypto';

// Set the base URL for the backend API
const API_URL = 'http://localhost:8000';

export default function AuthenticationPage() {
  const [activeTab, setActiveTab] = useState<string | null>('login');
  const router = useRouter();

  const form = useForm({
    initialValues: {
      email: '',
      password: '',
      confirmPassword: '',
      terms: false,
    },
    validate: (values) => {
        if (activeTab === 'register') {
            if (values.password !== values.confirmPassword) {
                return { confirmPassword: 'Passwords do not match' };
            }
            if (!values.terms) {
                return { terms: 'You must accept the terms and conditions' };
            }
        }
        return {};
    }
  });

  const handleRegister = async (values: any) => {
    try {
        await axios.post(`${API_URL}/auth/register`, {
            email: values.email,
            password: values.password,
        });
        notifications.show({
            title: 'Registration successful',
            message: 'You can now log in with your new account.',
            color: 'green',
        });
        setActiveTab('login');
        form.reset();
    } catch (error: any) {
        notifications.show({
            title: 'Registration failed',
            message: error.response?.data?.detail || 'An unexpected error occurred.',
            color: 'red',
        });
    }
  };

  const handleLogin = async (values: any) => {
    try {
        const response = await axios.post(`${API_URL}/auth/login`, new URLSearchParams({
            username: values.email,
            password: values.password,
        }), {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        });

        const { access_token } = response.data;
        useAuthStore.getState().setToken(access_token);
        notifications.show({
            title: 'Login successful',
            message: 'Welcome back!',
            color: 'green',
        });
        router.push('/dashboard');
    } catch (error: any) {
        notifications.show({
            title: 'Login failed',
            message: error.response?.data?.detail || 'Incorrect email or password.',
            color: 'red',
        });
    }
  };

  return (
    <Container size={420} my={40}>
      <Title ta="center">
        Welcome!
      </Title>
      <Text c="dimmed" size="sm" ta="center" mt={5}>
        Please log in or create an account to continue.
      </Text>

      <Paper withBorder shadow="md" p={30} mt={30} radius="md">
        <Tabs value={activeTab} onChange={setActiveTab}>
            <Tabs.List grow>
                <Tabs.Tab value="login">Login</Tabs.Tab>
                <Tabs.Tab value="register">Register</Tabs.Tab>
            </Tabs.List>

            <Tabs.Panel value="login" pt="xs">
                <form onSubmit={form.onSubmit(handleLogin)}>
                    <TextInput label="Email" placeholder="you@mantine.dev" required {...form.getInputProps('email')} />
                    <PasswordInput label="Password" placeholder="Your password" required mt="md" {...form.getInputProps('password')} />
                    <Group justify="space-between" mt="lg">
                        <Anchor component="button" size="sm">
                            Forgot password?
                        </Anchor>
                    </Group>
                    <Button fullWidth mt="xl" type="submit">
                        Sign in
                    </Button>
                </form>
            </Tabs.Panel>

            <Tabs.Panel value="register" pt="xs">
                <form onSubmit={form.onSubmit(handleRegister)}>
                    <TextInput label="Email" placeholder="you@mantine.dev" required {...form.getInputProps('email')} />
                    <PasswordInput label="Password" placeholder="Your password" required mt="md" {...form.getInputProps('password')} />
                    <PasswordInput label="Confirm Password" placeholder="Confirm password" required mt="md" {...form.getInputProps('confirmPassword')} />
                    <Checkbox label="I accept terms and conditions" required mt="md" {...form.getInputProps('terms', { type: 'checkbox' })} />
                    <Button fullWidth mt="xl" type="submit">
                        Register
                    </Button>
                </form>
            </Tabs.Panel>
        </Tabs>
      </Paper>
    </Container>
  );
}