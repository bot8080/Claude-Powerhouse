# App Name

> A React Native + Expo project scaffolded using [MultiAgents-Powerhouse](https://github.com/bot8080/MultiAgents-Powerhouse).

This project was created with:
```bash
npx powerhouse init my-app --stack expo
```

For full documentation on the development workflow, see the [MultiAgents-Powerhouse README](https://github.com/bot8080/MultiAgents-Powerhouse).

---

## Quick Start

```bash
npm install --legacy-peer-deps
cp .env.example .env  # fill in your Firebase/Stripe keys
npx expo start --lan
```

## Prerequisites

- Node.js 20+
- npm
- Expo CLI (`npx expo`)
- Android phone with Expo Go (or emulator)

## Development

```bash
npm start              # Start dev server
npm run typecheck      # TypeScript check
npm run lint           # Lint
npm run format         # Format with Prettier
npm test               # Run tests
```

## Project Structure

```
app/                    # Expo Router routes
src/
├── components/         # Reusable UI
├── constants/          # Colors, config
├── context/            # React contexts
├── hooks/              # Custom hooks
├── services/           # API services
├── types/              # TypeScript types
└── utils/              # Utilities
```

## Architecture

See `docs/ARCHITECTURE.md` and `docs/CONVENTIONS.md` for full details.
