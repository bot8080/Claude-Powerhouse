# Project Conventions

## Coding Standards

- **TypeScript strict mode** — `no-explicit-any` is an error
- **No hardcoded hex colors** — import from `@constants/colors`
- **Use `Pressable`** — never `TouchableOpacity` or `TouchableHighlight`
- **Icons** — always from `@expo/vector-icons` (Ionicons)

## Path Aliases

| Alias | Maps to |
|-------|---------|
| `@/*` | `src/*` |
| `@components/*` | `src/components/*` |
| `@services/*` | `src/services/*` |
| `@hooks/*` | `src/hooks/*` |
| `@context/*` | `src/context/*` |
| `@constants/*` | `src/constants/*` |
| `@utils/*` | `src/utils/*` |

## Commit Convention

```
<type>(<scope>): <subject>

Types: feat | fix | chore | docs | refactor | test | perf | build | ci | style | revert
```

Examples:
- `feat(auth): add login screen`
- `fix(posts): handle empty state`
- `chore(deps): update expo SDK`

## Branch Naming

- `feature/<slug>` — New features
- `fix/<slug>` — Bug fixes
- `chore/<slug>` — Config, deps, tooling
- `docs/<slug>` — Documentation
- `release/v<version>` — Versioned releases

## Build Order (Layered Architecture)

1. **Foundation** — Types, constants, utilities
2. **Services** — API/backend service layer
3. **Context & Hooks** — State management, custom hooks
4. **Components** — Reusable UI components
5. **Screens** — Full screen implementations
6. **Backend Functions** — Serverless/cloud functions
7. **Infrastructure** — CI/CD, security rules, config
