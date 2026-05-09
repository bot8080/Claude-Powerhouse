import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  useCallback,
  useMemo,
  type ReactNode,
} from 'react';
import { Platform, PermissionsAndroid } from 'react-native';
import { type FirebaseAuthTypes } from '@react-native-firebase/auth';
import {
  onAuthStateChanged,
  signOut as firebaseSignOut,
  signInWithPhone as rnfbSignInWithPhone,
} from '@services/auth';

interface AuthState {
  firebaseUser: FirebaseAuthTypes.User | null;
  isLoading: boolean;
}

interface AuthActions {
  signOut: () => Promise<void>;
  signInWithPhone: (phone: string) => Promise<FirebaseAuthTypes.ConfirmationResult>;
  verifyOTP: (otp: string) => Promise<FirebaseAuthTypes.UserCredential>;
}

const AuthStateContext = createContext<AuthState | null>(null);
const AuthActionsContext = createContext<AuthActions | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [firebaseUser, setFirebaseUser] = useState<FirebaseAuthTypes.User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const confirmResultRef = useRef<FirebaseAuthTypes.ConfirmationResult | null>(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(async (fbUser) => {
      try {
        if (fbUser) {
          setFirebaseUser(fbUser);
        } else {
          setFirebaseUser(null);
        }
      } catch {
        setFirebaseUser(null);
      } finally {
        setIsLoading(false);
      }
    });
    return unsubscribe;
  }, []);

  const signOut = useCallback(async () => {
    await firebaseSignOut();
    setFirebaseUser(null);
  }, []);

  const signInWithPhone = useCallback(
    async (phone: string): Promise<FirebaseAuthTypes.ConfirmationResult> => {
      const result = await rnfbSignInWithPhone(phone);
      confirmResultRef.current = result;
      return result;
    },
    [],
  );

  const verifyOTP = useCallback(
    async (otp: string): Promise<FirebaseAuthTypes.UserCredential> => {
      if (!confirmResultRef.current) {
        throw new Error('No pending sign-in — call signInWithPhone first');
      }
      const credential = await confirmResultRef.current.confirm(otp);
      if (!credential) {
        throw new Error('OTP confirmation returned no credential');
      }
      return credential;
    },
    [],
  );

  const stateValue = useMemo(
    () => ({ firebaseUser, isLoading }),
    [firebaseUser, isLoading],
  );

  const actionsValue = useMemo(
    () => ({ signOut, signInWithPhone, verifyOTP }),
    [signOut, signInWithPhone, verifyOTP],
  );

  return (
    <AuthStateContext.Provider value={stateValue}>
      <AuthActionsContext.Provider value={actionsValue}>
        {children}
      </AuthActionsContext.Provider>
    </AuthStateContext.Provider>
  );
}

export function useAuthState(): AuthState {
  const ctx = useContext(AuthStateContext);
  if (!ctx) {
    throw new Error('useAuthState must be used within <AuthProvider>');
  }
  return ctx;
}

export function useAuthActions(): AuthActions {
  const ctx = useContext(AuthActionsContext);
  if (!ctx) {
    throw new Error('useAuthActions must be used within <AuthProvider>');
  }
  return ctx;
}

export function useAuth(): AuthState & AuthActions {
  return { ...useAuthState(), ...useAuthActions() };
}
