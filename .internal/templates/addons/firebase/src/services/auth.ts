import auth, { type FirebaseAuthTypes } from '@react-native-firebase/auth';

export type { FirebaseAuthTypes };

export function onAuthStateChanged(
  callback: (user: FirebaseAuthTypes.User | null) => void,
): () => void {
  return auth().onAuthStateChanged(callback);
}

export function signOut(): Promise<void> {
  return auth().signOut();
}

export function getCurrentUser(): FirebaseAuthTypes.User | null {
  return auth().currentUser;
}

export function signInWithPhone(
  phoneNumber: string,
): Promise<FirebaseAuthTypes.ConfirmationResult> {
  return auth().signInWithPhoneNumber(phoneNumber);
}
