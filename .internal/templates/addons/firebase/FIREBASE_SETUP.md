# Firebase Setup Guide

## Step 1: Create a Firebase Project

1. Go to https://console.firebase.google.com
2. Click **Create a project**
3. Enter your project name and follow the prompts
4. Choose whether to enable Google Analytics

## Step 2: Register Your App

### Web App (for Firestore JS SDK)
1. In Firebase Console, click **Add app** → **Web**
2. Copy the `firebaseConfig` values
3. Paste them into your `.env` file:
   ```
   EXPO_PUBLIC_FIREBASE_API_KEY=
   EXPO_PUBLIC_FIREBASE_AUTH_DOMAIN=
   EXPO_PUBLIC_FIREBASE_PROJECT_ID=
   EXPO_PUBLIC_FIREBASE_STORAGE_BUCKET=
   EXPO_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=
   EXPO_PUBLIC_FIREBASE_APP_ID=
   ```

### Android App (for native Firebase features)
1. Click **Add app** → **Android**
2. Enter your package name (e.g., `com.example.app`)
3. Download `google-services.json`
4. Place it at the project root

### iOS App (for native Firebase features)
1. Click **Add app** → **iOS**
2. Enter your bundle ID (e.g., `com.example.app`)
3. Download `GoogleService-Info.plist`
4. Place it in the `ios/` directory

## Step 3: Enable Phone Authentication

1. In Firebase Console, go to **Authentication** → **Sign-in method**
2. Enable **Phone** provider
3. Add test phone numbers for development:
   - Phone: `+15551234567` / Code: `123456`

## Step 4: Create Firestore Database

1. Go to **Firestore Database** → **Create database**
2. Choose a location close to your users (e.g., `northamerica-northeast1`)
3. Start in **test mode** (you'll deploy rules from the repo)

## Step 5: Enable Storage

1. Go to **Storage** → **Get started**
2. Choose a location
3. Start in **test mode** (deploy rules from the repo)

## Step 6: Deploy Rules & Functions

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# Initialize your project
firebase use --add

# Deploy Firestore rules
firebase deploy --only firestore

# Deploy Storage rules
firebase deploy --only storage

# Deploy Cloud Functions
cd functions && npm install && cd ..
firebase deploy --only functions
```
