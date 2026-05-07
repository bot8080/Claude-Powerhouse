<!-- CLAUDE.md — Expo stack-specific project context -->

# CLAUDE.md — Expo Project

## Hard Rules

1. Read `docs/CONVENTIONS.md` before implementing any feature
2. Read `docs/ARCHITECTURE.md` to understand project structure
3. All colors from `@constants/colors` — never hardcode hex
4. Use `Pressable` (not `TouchableOpacity`)
5. Icons from `@expo/vector-icons` (Ionicons)
6. TypeScript strict mode — no `any`
7. Path aliases: `@/`, `@components/`, `@services/`, `@hooks/`, `@context/`, `@constants/`, `@utils/`

## Tech Stack

- React Native + Expo SDK 54, TypeScript strict
- Expo Router 6 (file-based routing)
- Path aliases with babel-plugin-module-resolver