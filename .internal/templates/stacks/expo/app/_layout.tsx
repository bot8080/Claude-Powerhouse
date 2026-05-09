import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import ErrorBoundary from '@components/ErrorBoundary';

export default function RootLayout() {
  return (
    <ErrorBoundary>
      <StatusBar style="dark" />
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="(auth)" />
        <Stack.Screen name="(tabs)" />
      </Stack>
    </ErrorBoundary>
  );
}
