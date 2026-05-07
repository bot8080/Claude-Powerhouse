import React from 'react';
import { render } from '@testing-library/react-native';
import { AuthProvider, useAuthState } from '@context/AuthContext';

function TestConsumer() {
  const { isLoading } = useAuthState();
  return <>{isLoading ? 'loading' : 'ready'}</>;
}

describe('AuthProvider', () => {
  it('renders children', () => {
    const { getByText } = render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );
    expect(getByText(/loading|ready/)).toBeTruthy();
  });
});
