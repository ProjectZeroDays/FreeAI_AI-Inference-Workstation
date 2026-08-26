---
name: setup-deployment
description: Complete setup and deployment workflow for Next.js applications with Prisma, Capacitor mobile apps, and production hosting. Use when the user wants to set up a new project, deploy to production, configure environments, run database migrations, or prepare an app for release. Triggers on: "setup the app", "deploy the app", "install dependencies", "run migrations", "configure environment", "build for production", "capacitor sync", "prepare for release", "run the setup script".
license: Complete terms in LICENSE.txt
---

# Setup & Deployment

This skill covers the complete setup, configuration, and deployment workflow for Next.js applications with Prisma ORM, Capacitor mobile apps, and production hosting.

## Setup Script

The interactive setup script (`setup.ps1`) provides a menu-driven workflow:

```powershell
# Run the setup wizard
.\setup.ps1

# Or run specific steps manually
npm install                    # Install all dependencies
npx prisma generate           # Generate Prisma client
npx prisma db push           # Push schema to database (dev)
npx prisma migrate deploy    # Run migrations (prod)
npm run build                # Production build
npx cap sync                 # Sync Capacitor projects
```

## Database Setup

### Option 1: Docker (Local Development)
```bash
docker-compose up -d
# Database available at: postgresql://postgres:postgres@localhost:5432/massage_connect
```

### Option 2: Supabase (Recommended for Production)
1. Create project at https://supabase.com/dashboard
2. Copy connection string from Settings > Database
3. Update `.env.local`:
```
DATABASE_URL="postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres"
```

### Option 3: Neon
1. Create project at https://neon.tech
2. Copy connection string
3. Update `.env.local`

## Environment Configuration

Create `.env.local` from template:
```bash
cp .env.example .env.local
```

Required variables:
```env
DATABASE_URL="postgresql://..."
JWT_SECRET="your-random-secret-min-32-chars"
JWT_EXPIRES_IN="7d"
REFRESH_TOKEN_SECRET="your-random-refresh-secret"
REFRESH_TOKEN_EXPIRES_IN="30d"
STRIPE_SECRET_KEY="sk_test_..."
STRIPE_WEBHOOK_SECRET="whsec_..."
RESEND_API_KEY="re_..."
NEXT_PUBLIC_APP_URL="https://yourdomain.com"
NODE_ENV="production"
```

## Deployment Options

### Vercel (Recommended for Next.js)
```json
// vercel.json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "outputDirectory": ".next",
  "regions": ["iad1", "sfo1", "fra1", "syd1"],
  "crons": [
    {
      "path": "/api/system/cron",
      "schedule": "0 2 * * *"
    }
  ]
}
```

Deploy:
```bash
npx vercel --prod
```

### Docker
```bash
docker-compose up -d --build
```

### Self-Hosted
```bash
npm run build
npm start
# Requires: Node.js 18+, PostgreSQL
```

## Mobile App Setup

### Android
```bash
npm install @capacitor/android
npx cap add android
npx cap sync
npx cap open android  # Opens in Android Studio
```

### iOS
```bash
npm install @capacitor/ios
npx cap add ios
npx cap sync
npx cap open ios  # Opens in Xcode
```

### Build Release
```bash
# Build web assets
npm run build

# Sync to native projects
npx cap sync

# Generate icons
node scripts/generate-icons.js

# Build Android AAB
npx cap build android

# Build iOS
npx cap build ios
```

## Pre-Production Checklist

### Security
- [ ] Change all default secrets in `.env.local`
- [ ] Enable CSRF protection
- [ ] Set up rate limiting on sensitive endpoints
- [ ] Enable HTTPS only
- [ ] Configure CORS properly

### Performance
- [ ] Enable Next.js image optimization
- [ ] Set up CDN for static assets
- [ ] Configure database connection pooling
- [ ] Enable compression

### Monitoring
- [ ] Set up Sentry error tracking
- [ ] Configure health check endpoint
- [ ] Set up daily cron jobs
- [ ] Enable logging

### App Store
- [ ] Generate app icons (1024x1024)
- [ ] Create splash screens
- [ ] Update AndroidManifest.xml
- [ ] Update iOS Info.plist
- [ ] Configure push notifications
- [ ] Generate screenshots for stores

## Post-Deployment

1. Run database migrations:
```bash
npx prisma migrate deploy
```

2. Verify health check:
```bash
curl https://yourdomain.com/api/health
```

3. Test critical flows:
   - Registration
   - Login
   - Booking
   - Payment

4. Set up monitoring alerts
5. Configure backup strategy
6. Document operational procedures
