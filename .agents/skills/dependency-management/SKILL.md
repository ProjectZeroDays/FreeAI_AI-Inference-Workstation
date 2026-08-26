---
name: dependency-management
description: Package dependency management, version resolution, lock files, security auditing, and monorepo dependency strategies. Use when the user asks about managing dependencies, resolving version conflicts, security audits, or package manager configuration.
---

# Dependency Management

## Package Manager Comparison

| Feature | npm | yarn | pnpm | bun |
|---------|-----|------|------|-----|
| Lock file | package-lock.json | yarn.lock | pnpm-lock.yaml | bun.lockb |
| Workspace | workspaces | workspaces | pnpm-workspace.yaml | workspaces |
| Node modules | Flat | Flat | Strict | Flat |
| Speed | Baseline | Fast | Fastest | Fastest |

## Versioning (SemVer)

```
MAJOR.MINOR.PATCH
  │      │      │
  │      │      └── Bug fixes (backwards compatible)
  │      └── New features (backwards compatible)
  └── Breaking changes
```

### Version Ranges
```json
{
  "dependencies": {
    "lodash": "^4.17.21",     // >=4.17.21 <5.0.0
    "express": "~4.18.0",     // >=4.18.0 <4.19.0
    "react": "18.2.0",        // Exactly 18.2.0
    "typescript": ">=5.0.0",  // 5.0.0 or higher
    "my-lib": "latest"        // Always latest
  }
}
```

## npm

```bash
# Install
npm install                    # Install all deps
npm install express            # Add dependency
npm install -D typescript      # Add dev dependency
npm install -g typescript      # Global install

# Remove
npm uninstall express

# Update
npm update                     # Update within range
npm update express             # Update specific package
npm outdated                   # Check outdated

# Audit
npm audit                      # Check vulnerabilities
npm audit fix                  # Auto-fix
npm audit fix --force          # Force fix (breaking)

# Scripts
npm run build
npm run test
npm run lint
```

## yarn

```bash
# Install
yarn install                   # Install all deps
yarn add express               # Add dependency
yarn add -D typescript         # Add dev dependency

# Remove
yarn remove express

# Update
yarn upgrade express           # Update to latest in range
yarn upgrade-interactive       # Interactive update

# Audit
yarn audit
```

## pnpm

```bash
# Install
pnpm install                   # Install all deps
pnpm add express               # Add dependency
pnpm add -D typescript         # Add dev dependency

# Remove
pnpm remove express

# Update
pnpm update                    # Update all
pnpm update express            # Update specific

# Audit
pnpm audit

# Workspace
pnpm add lodash --filter @repo/utils
pnpm add -Dw typescript        # Root devDep
```

## Resolving Conflicts

```bash
# Delete and reinstall
rm -rf node_modules package-lock.json
npm install

# Force resolution (npm)
# package.json
{
  "overrides": {
    "lodash": "4.17.21"
  }
}

# Force resolution (yarn)
# package.json
{
  "resolutions": {
    "lodash": "4.17.21"
  }
}

# Force resolution (pnpm)
# package.json
{
  "pnpm": {
    "overrides": {
      "lodash": "4.17.21"
    }
  }
}
```

## Lock Files

- **Always commit lock files** to version control
- **Never manually edit** lock files
- **Use same package manager** across team
- **Regenerate** when switching package managers

```bash
# Check lock file integrity
npm ci                         # Clean install from lock file
yarn install --frozen-lockfile
pnpm install --frozen-lockfile
```

## Security Best Practices

```bash
# Check for vulnerabilities
npm audit
yarn audit
pnpm audit

# Fix automatically
npm audit fix
npm audit fix --force          # May include breaking changes

# Check specific package
npm audit lodash
```

## Dependency Hygiene

```bash
# Find unused dependencies
npx depcheck

# Bundle size analysis
npx webpack-bundle-analyzer stats.json
npx source-map-explorer dist/main.js.map

# Check for duplicates
npx yarn-deduplicate --list
pnpm dedupe
```

## Publishing Packages

```json
// package.json
{
  "name": "@myorg/my-package",
  "version": "1.2.3",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "files": ["dist", "README.md"],
  "publishConfig": {
    "access": "public",
    "registry": "https://registry.npmjs.org"
  },
  "scripts": {
    "prepublishOnly": "npm run build"
  }
}
```

```bash
# Publish
npm publish
npm publish --access public    # For scoped packages

# Version bump
npm version patch             # 1.2.3 -> 1.2.4
npm version minor             # 1.2.3 -> 1.3.0
npm version major             # 1.2.3 -> 2.0.0
```

## Best Practices

1. Commit lock files
2. Use exact versions in applications
3. Use ranges in libraries
4. Regularly update dependencies
5. Audit for security vulnerabilities
6. Pin node version (.nvmrc, .node-version)
7. Use workspace protocols in monorepos
8. Remove unused dependencies
9. Check bundle size impact
10. Use `npm ci` in CI/CD (not `npm install`)
