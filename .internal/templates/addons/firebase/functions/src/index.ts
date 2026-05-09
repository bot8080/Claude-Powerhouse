import { onDocumentCreated } from 'firebase-functions/v2/firestore';
import { onCall } from 'firebase-functions/v2/https';
import { getFirestore } from 'firebase-admin/firestore';
import { initializeApp } from 'firebase-admin/app';

initializeApp();

const db = getFirestore();

// Example: Auto-create user profile on sign up
export const onUserCreated = onDocumentCreated('users/{userId}', async (event) => {
  const snapshot = event.data;
  if (!snapshot) return;

  const userData = snapshot.data();
  const uid = event.params.userId;

  await db.collection('users').doc(uid).update({
    createdAt: new Date(),
    updatedAt: new Date(),
    ...userData,
  });
});

// Example: Hello world callable function
export const helloWorld = onCall(async () => {
  return { message: 'Hello from Firebase!' };
});
