---
name: fullstack-platform-completion
description: End-to-end platform completion workflow for Next.js applications. Use when the user wants to fix broken features, create missing pages, implement dashboard tabs, connect APIs to UI components, or complete an incomplete full-stack application. Triggers on: "complete the app", "fix everything", "finish the platform", "implement all features", "wire up APIs", "connect frontend to backend", "fix broken flows", "missing pages", "stub features", "incomplete components".
license: Complete terms in LICENSE.txt
---

# Full-Stack Platform Completion

This skill provides a systematic approach to completing a full-stack Next.js application by identifying and fixing all broken, incomplete, or stub features.

## Phase 1: Audit & Inventory

Run this audit to identify all incomplete features:

```bash
# 1. Find all stub/mock data patterns
grep -r "TODO\|FIXME\|HACK\|STUB\|PLACEHOLDER\|mock\|stub\|placeholder\|hardcoded\|not implemented" src/ --include="*.ts" --include="*.tsx" | grep -v node_modules

# 2. Find all API routes and check if they exist for every referenced endpoint
find src/app/api -name "route.ts" | wc -l

# 3. Find all page routes and check for missing page.tsx files
find src/app -type d | while read dir; do
  if [ ! -f "$dir/page.tsx" ] && [ ! -f "$dir/page.ts" ]; then
    echo "MISSING PAGE: $dir"
  fi
done

# 4. Find all component imports and check for missing files
grep -r "import.*from" src/ --include="*.tsx" | grep -v node_modules | grep -v ".next" | cut -d'"' -f2 | sort -u
```

## Phase 2: Critical Flow Fixes

### 2.1 Fix Authentication Flows
Check these endpoints are fully wired:
- `/api/auth/register` — handles all form fields including new consent checkboxes
- `/api/auth/login` — returns proper user object with profile data
- `/api/auth/logout` — clears session cookies
- `/api/auth/me` — returns full user profile
- `/api/auth/reset-password` — must NOT use `withAuth` wrapper (unauthenticated endpoint)

### 2.2 Fix Registration/Signup Flow
Common issues:
- Signup form sends `FormData` but API expects `JSON` — align the format
- Missing consent checkboxes not validated server-side
- Therapist verification doesn't create `VerificationDoc` records
- Password not hashed before storage

### 2.3 Fix Dashboard Tab Integration
Each GoldDashboard tab must:
- Accept `therapistId` prop
- Fetch real data from API (no hardcoded numbers)
- Handle loading and error states
- Save changes back to API on submit

## Phase 3: Missing Page Creation

### 3.1 Dynamic Route Pages
Create these missing pages with real data fetching:

**`src/app/therapist/[id]/page.tsx`**
```tsx
'use client';
import { useRouter, useSearchParams } from 'next/navigation';
// Fetch therapist data from /api/therapists/[id]
// Show profile, services with discounts, book button
// Tabs: overview, services, reviews, photos
```

**`src/app/booking/[id]/page.tsx`**
```tsx
'use client';
import { useRouter, useSearchParams } from 'next/navigation';
// Multi-step booking: service selection → date/time → client details
// Submit to /api/bookings
// Redirect to success page
```

**`src/app/city/[city]/page.tsx`**
```tsx
// Server component with SSR
// Fetch therapists by city from /api/therapists?city=
// Revalidate: 300s
```

### 3.2 Blog & Content Pages
- `/blog` — List published posts from `/api/blog`
- `/blog/[slug]` — Single post with view increment

## Phase 4: API-UI Connection

### 4.1 Services & Discounts
```tsx
// ServicesTab must:
// 1. Fetch from /api/therapists/services (GET)
// 2. Create via POST with { name, duration, price, discount, discountType }
// 3. Update via PUT with { id, ...fields }
// 4. Delete via DELETE with ?id= query param
// 5. Show effective price: price - (discount% or fixed amount)
```

### 4.2 Finance Tab
```tsx
// FinanceTab must:
// 1. Fetch financial data from /api/financial?userId=
// 2. Show real income, expenses, net profit
// 3. Add expense via POST /api/financial/expenses
// 4. Export CSV from existing expense data
```

### 4.3 Photo Studio
```tsx
// PhotoStudioTab must:
// 1. Fetch photos from /api/therapists/[id] include: photos
// 2. Upload via POST /api/photos/upload (FormData)
// 3. Delete via DELETE /api/photos/[id]
// 4. AI edit via POST /api/photo-editor
```

## Phase 5: Build Verification

```bash
# 1. Generate Prisma client
npx prisma generate

# 2. Run type check
npx tsc --noEmit

# 3. Run tests
npx vitest run

# 4. Build production
npm run build

# 5. Verify no TypeScript errors
# Fix any "error TS" or "Type error" messages
```

## Phase 6: Common Fixes Quick Reference

| Symptom | Fix |
|---------|-----|
| `Property 'user' does not exist on type 'NextRequest'` | Cast: `(req as any).user` |
| `Property 'query' does not exist on type 'AppRouterInstance'` | Use `useSearchParams()` instead of `router.query` |
| `discount` field missing from Prisma | Add to schema, run `npx prisma migrate dev` |
| Form sends FormData but API expects JSON | Change to `JSON.stringify()` or fix API to parse FormData |
| Static page can't access `request.url` | Add `export const dynamic = 'force-dynamic'` |
| API route needs auth but shouldn't require it | Remove `withAuth` wrapper |

## Files to Create/Modify

```
src/app/
├── booking/[id]/page.tsx          # NEW: Booking flow
├── booking/[id]/success/page.tsx  # NEW: Booking confirmation
├── city/[city]/page.tsx           # NEW: City listings
├── therapist/[id]/page.tsx        # NEW: Therapist detail
├── blog/page.tsx                  # NEW: Blog index
└── api/
    ├── therapists/services/route.ts    # NEW: Service CRUD
    ├── financial/expenses/route.ts     # NEW: Expense management
    ├── system/health/route.ts          # NEW: System health
    └── system/optimize/route.ts        # NEW: Auto-cleanup

src/components/dashboard/GoldDashboard/
├── ServicesTab.tsx       # FIXED: Real API integration
├── FinanceTab.tsx        # FIXED: Real API integration
├── PhotoStudioTab.tsx    # FIXED: Real upload/delete
├── MarketingTab.tsx      # FIXED: AI generation + campaigns
└── AISettingsTab.tsx     # FIXED: Config persistence
```
