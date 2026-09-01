---
name: monorepo-management
description: Monorepo architecture with Turborepo, Nx, pnpm workspaces, and workspace protocols. Use when the user asks about setting up monorepos, managing multiple packages, shared dependencies, build caching, or workspace configuration.
---

# Monorepo Management

## Project Structure

```
monorepo/
├── apps/
│   ├── web/              # Next.js app
│   ├── api/              # Express/Fastify API
│   └── mobile/           # React Native
├── packages/
│   ├── ui/               # Shared UI components
│   ├── utils/            # Shared utilities
│   ├── config/           # Shared configs (tsconfig, eslint)
│   └── db/               # Database schema & migrations
├── package.json
├── pnpm-workspace.yaml
├── turbo.json
└── tsconfig.base.json
```

## pnpm Workspace Setup

```yaml
# pnpm-workspace.yaml
packages:
  - "apps/*"
  - "packages/*"
```

```json
// package.json (root)
{
  "name": "monorepo",
  "private": true,
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "lint": "turbo run lint",
    "test": "turbo run test"
  },
  "devDependencies": {
    "turbo": "^2.0.0"
  }
}
```

## Turborepo Config

```json
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {},
    "test": {
      "dependsOn": ["build"]
    }
  }
}
```

## Internal Package References

```json
// packages/ui/package.json
{
  "name": "@repo/ui",
  "version": "0.0.0",
  "main": "./src/index.tsx",
  "types": "./src/index.tsx",
  "dependencies": {
    "@repo/utils": "workspace:*"
  }
}
```

```json
// apps/web/package.json
{
  "name": "@repo/web",
  "dependencies": {
    "@repo/ui": "workspace:*",
    "@repo/utils": "workspace:*"
  }
}
```

## TypeScript Project References

```json
// tsconfig.base.json (root)
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "composite": true
  }
}
```

```json
// apps/web/tsconfig.json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src"],
  "references": [
    { "path": "../../packages/ui" },
    { "path": "../../packages/utils" }
  ]
}
```

## Shared ESLint Config

```javascript
// packages/config/eslint/index.js
module.exports = {
  extends: [
    "eslint:recommended",
    "typescript-eslint/recommended",
    "prettier"
  ],
  rules: {
    "no-console": "warn",
    "no-unused-vars": "off",
    "@typescript-eslint/no-unused-vars": ["error", { argsIgnorePattern: "^_" }]
  }
};
```

```json
// apps/web/.eslintrc.json
{
  "extends": ["@repo/config/eslint"]
}
```

## Nx Alternative Setup

```json
// nx.json
{
  "targetDefaults": {
    "build": {
      "dependsOn": ["^build"],
      "inputs": ["production", "^production"]
    }
  },
  "namedInputs": {
    "default": ["{projectRoot}/**/*"],
    "production": ["!{projectRoot}/**/*.spec.ts"]
  }
}
```

```bash
# Nx commands
npx nx run web:build        # Build specific app
npx nx run-many -t build    # Build all
npx nx affected -t test     # Test affected only
npx nx graph                # Visualize dependencies
```

## Turborepo Filters

```bash
# Build only web and its dependencies
turbo run build --filter=web

# Build web and everything it depends on
turbo run build --filter=web...

# Build everything except mobile
turbo run build --filter=!mobile

# Run dev in parallel for specific packages
turbo run dev --filter=@repo/ui --filter=@repo/web
```

## Adding a New Package

```bash
# Create package directory
mkdir packages/my-package

# Initialize
cd packages/my-package
pnpm init

# Add to workspace (already handled by pnpm-workspace.yaml)

# Reference from app
cd apps/web
pnpm add @repo/my-package --workspace
```

## Dependency Management

```bash
# Add dep to specific package
pnpm add lodash --filter @repo/utils

# Add devDep to root
pnpm add -Dw typescript

# Update all packages
pnpm update -r

# Check outdated
pnpm outdated -r
```

## Common Issues

### Circular Dependencies
```bash
# Detect
npx madge --circular packages/*/src

# Fix: Extract shared code to a new package
```

### Build Order
```json
// turbo.json - ensure correct order
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"]
    }
  }
}
```

### Version Management
```bash
# Changesets for versioning
pnpm add -Dw @changesets/cli
pnpm changeset        # Create changeset
pnpm changeset version # Bump versions
pnpm changeset publish # Publish
```
