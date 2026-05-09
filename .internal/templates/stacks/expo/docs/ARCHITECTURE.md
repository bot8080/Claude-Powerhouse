# Architecture

## Project Structure

```
├── app/                    # Expo Router file-based routes
│   ├── _layout.tsx         # Root layout (providers, error boundary)
│   ├── (auth)/             # Auth group (login, onboarding)
│   ├── (tabs)/             # Tab navigator (main app screens)
│   └── +not-found.tsx      # 404 catch-all
├── src/
│   ├── components/         # Reusable UI components
│   ├── constants/          # Colors, layout tokens, config
│   ├── context/            # React context providers
│   ├── hooks/              # Custom hooks
│   ├── services/           # API/backend service layer
│   ├── types/              # TypeScript type definitions
│   ├── utils/              # Utility functions
│   └── __tests__/          # Test files
├── docs/                   # Project documentation
├── functions/              # Firebase Cloud Functions (optional)
├── assets/                 # Static assets (images, fonts)
└── scripts/                # Utility scripts
```

## Layered Build Order

1. **Foundation** — `src/types/`, `src/constants/`, `src/utils/`
2. **Services** — `src/services/` (Firebase, API clients, etc.)
3. **Context & Hooks** — `src/context/`, `src/hooks/`
4. **Components** — `src/components/`
5. **Screens** — `app/` routes
6. **Backend** — `functions/` (if using Firebase)
7. **Infrastructure** — `firestore.rules`, CI, config

## Data Flow

```
Screen → Hook/Context → Service → Backend API → Firestore/DB
                             ↕
                        State updates ← realtime listeners
```
