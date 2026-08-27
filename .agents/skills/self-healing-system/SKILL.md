---
name: self-healing-system
description: Autonomous system health monitoring, self-healing, resource optimization, and self-improvement workflows. Use when the user wants to implement automatic system health checks, auto-fix issues, optimize resources, reduce costs, schedule daily maintenance, or create a self-managing application. Triggers on: "self-healing", "auto-fix", "system health", "resource optimization", "cost reduction", "automated maintenance", "system monitoring", "self-improving", "auto-optimization", "daily workflow", "resource analysis", "load balancing".
license: Complete terms in LICENSE.txt
---

# Self-Healing System

This skill provides workflows for implementing autonomous system health monitoring, self-healing capabilities, resource optimization, and AI-powered recommendations.

## System Health API

Create `src/app/api/system/health/route.ts`:

```typescript
import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET() {
  const now = new Date();
  const dayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
  const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

  const [
    totalUsers, activeUsers, newUsersToday, newUsersWeek,
    totalTherapists, approvedTherapists, activeSubscriptions,
    totalBookings, bookingsToday, bookingsWeek,
    totalRevenue, revenueToday, revenueWeek, revenueMonth,
    pendingVerifications, rejectedPhotos, activeReviews,
    subscriptionCount,
  ] = await Promise.all([
    prisma.user.count(),
    prisma.user.count({ where: { isVerified: true } }),
    prisma.user.count({ where: { createdAt: { gte: dayAgo } } }),
    prisma.user.count({ where: { createdAt: { gte: weekAgo } } }),
    prisma.therapistProfile.count(),
    prisma.therapistProfile.count({ where: { isApproved: true } }),
    prisma.therapistProfile.count({ where: { subscriptionActive: true } }),
    prisma.booking.count(),
    prisma.booking.count({ where: { createdAt: { gte: dayAgo } } }),
    prisma.booking.count({ where: { createdAt: { gte: weekAgo } } }),
    prisma.payment.aggregate({ _sum: { amount: true }, where: { status: 'COMPLETED' } }),
    prisma.payment.aggregate({ _sum: { amount: true }, where: { status: 'COMPLETED', createdAt: { gte: dayAgo } } }),
    prisma.payment.aggregate({ _sum: { amount: true }, where: { status: 'COMPLETED', createdAt: { gte: weekAgo } } }),
    prisma.payment.aggregate({ _sum: { amount: true }, where: { status: 'COMPLETED', createdAt: { gte: monthAgo } } }),
    prisma.verificationDoc.count({ where: { status: 'PENDING' } }),
    prisma.photo.count({ where: { status: 'REJECTED' } }),
    prisma.review.count({ where: { status: 'APPROVED' } }),
    prisma.subscription.count({ where: { status: 'ACTIVE' } }),
  ]);

  const recommendations: string[] = [];
  if (pendingVerifications > 20) recommendations.push('High verification backlog. Prioritize admin review.');
  if (rejectedPhotos > 50) recommendations.push('High photo rejection rate. Update upload guidelines.');
  if (newUsersToday === 0) recommendations.push('No new users today. Check marketing channels.');
  if (activeSubscriptions < totalTherapists * 0.3) recommendations.push('Low subscription adoption. Consider promotions.');
  if (bookingsToday === 0 && approvedTherapists > 0) recommendations.push('No bookings despite active therapists. Check search visibility.');

  return NextResponse.json({
    success: true,
    timestamp: now.toISOString(),
    resourceUsage: {
      cpu: process.cpuUsage(),
      memory: process.memoryUsage(),
      uptime: process.uptime(),
    },
    dbHealth: {
      totalUsers, activeUsers, newUsersToday, newUsersWeek,
      totalTherapists, approvedTherapists, activeSubscriptions,
      totalBookings, bookingsToday, bookingsWeek,
      totalRevenue: totalRevenue._sum.amount || 0,
      revenueToday: revenueToday._sum.amount || 0,
      revenueWeek: revenueWeek._sum.amount || 0,
      revenueMonth: revenueMonth._sum.amount || 0,
      pendingVerifications, rejectedPhotos, activeReviews, subscriptionCount,
    },
    recommendations,
  });
}
```

## Self-Healing/Optimization API

Create `src/app/api/system/optimize/route.ts`:

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  const body = await request.json();
  const { action } = body;

  if (action === 'optimize') {
    const result = await runOptimization();
    return NextResponse.json({ success: true, result });
  }

  if (action === 'analyze') {
    const analysis = await runAnalysis();
    return NextResponse.json({ success: true, analysis });
  }

  return NextResponse.json({ error: 'Unknown action' }, { status: 400 });
}

async function runOptimization() {
  const now = new Date();
  const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

  const [bookings, notifications, sessions, photos] = await Promise.all([
    prisma.booking.deleteMany({
      where: {
        status: { in: ['PENDING', 'THERAPIST_PENDING'] },
        startTime: { lt: now },
        createdAt: { lt: weekAgo },
      },
    }),
    prisma.notification.deleteMany({
      where: {
        read: true,
        createdAt: { lt: new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000) },
      },
    }),
    prisma.session.deleteMany({
      where: { expiresAt: { lt: now } },
    }),
    prisma.photo.deleteMany({
      where: {
        status: 'REJECTED',
        createdAt: { lt: new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000) },
      },
    }),
  ]);

  return {
    cleanedBookings: bookings.count,
    cleanedNotifications: notifications.count,
    cleanedSessions: sessions.count,
    cleanedPhotos: photos.count,
  };
}

async function runAnalysis() {
  const now = new Date();
  const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

  const [newUsers, bookings, revenue, pendingVerifications, inactiveTherapists] = await Promise.all([
    prisma.user.count({ where: { createdAt: { gte: weekAgo } } }),
    prisma.booking.count({ where: { createdAt: { gte: weekAgo } } }),
    prisma.payment.aggregate({ _sum: { amount: true }, where: { status: 'COMPLETED', createdAt: { gte: weekAgo } } }),
    prisma.verificationDoc.count({ where: { status: 'PENDING' } }),
    prisma.therapistProfile.count({ where: { subscriptionActive: false, isApproved: true } }),
  ]);

  const recommendations: string[] = [];
  if (pendingVerifications > 10) recommendations.push(`High backlog: ${pendingVerifications} pending verifications.`);
  if (inactiveTherapists > 0) recommendations.push(`${inactiveTherapists} therapists with inactive subscriptions.`);
  if (newUsers < 5) recommendations.push('Low new user growth this week.');

  return {
    weekStats: { newUsers, bookings, revenue: revenue._sum.amount || 0 },
    pendingVerifications,
    inactiveTherapists,
    recommendations,
    lastRun: now.toISOString(),
  };
}
```

## Daily Cron Job

Create `src/app/api/system/cron/route.ts`:

```typescript
import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST() {
  const now = new Date();
  const dayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
  const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

  try {
    // Cleanup
    const [staleBookings, staleNotifications, staleSessions] = await Promise.all([
      prisma.booking.deleteMany({
        where: {
          status: { in: ['PENDING', 'THERAPIST_PENDING'] },
          startTime: { lt: now },
          createdAt: { lt: weekAgo },
        },
      }),
      prisma.notification.deleteMany({
        where: {
          read: true,
          createdAt: { lt: new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000) },
        },
      }),
      prisma.session.deleteMany({ where: { expiresAt: { lt: now } } }),
    ]);

    // Analytics
    const [newUsers, bookings, revenue, pendingVerifications, activeSubscriptions, errorReports] = await Promise.all([
      prisma.user.count({ where: { createdAt: { gte: dayAgo } } }),
      prisma.booking.count({ where: { createdAt: { gte: dayAgo } } }),
      prisma.payment.aggregate({ _sum: { amount: true }, where: { status: 'COMPLETED', createdAt: { gte: dayAgo } } }),
      prisma.verificationDoc.count({ where: { status: 'PENDING' } }),
      prisma.therapistProfile.count({ where: { subscriptionActive: true } }),
      prisma.bugReport.count({ where: { createdAt: { gte: dayAgo } } }),
    ]);

    // Generate recommendations
    const recommendations: string[] = [];
    if (pendingVerifications > 20) recommendations.push('High verification backlog');
    if (newUsers === 0) recommendations.push('No new users today');
    if (activeSubscriptions === 0) recommendations.push('No active subscriptions');

    // Store daily report
    await prisma.$executeRaw`
      INSERT INTO daily_reports (new_users, bookings, revenue, recommendations, generated_at)
      VALUES (${newUsers}, ${bookings}, ${revenue._sum.amount || 0}, ${JSON.stringify(recommendations)}, ${now.toISOString()})
    `;

    return NextResponse.json({
      success: true,
      dailyReport: {
        newUsers,
        bookings,
        revenue: revenue._sum.amount || 0,
        pendingVerifications,
        activeSubscriptions,
        errorReports,
      },
      cleanup: { staleBookings: staleBookings.count, staleNotifications: staleNotifications.count, staleSessions: staleSessions.count },
      timestamp: now.toISOString(),
    });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
```

## Vercel Cron Configuration

Add to `vercel.json`:
```json
{
  "crons": [
    {
      "path": "/api/system/cron",
      "schedule": "0 2 * * *"
    }
  ]
}
```

## Self-Healing Script

Create `scripts/self-healing.js`:

```javascript
const { execSync } = require('child_process');

class SelfHealingSystem {
  async healthCheck() {
    const checks = { database: false, api: false, build: false, tests: false };
    
    try {
      const res = await fetch('http://localhost:3000/api/health');
      checks.api = res.ok;
    } catch { checks.api = false; }

    try {
      execSync('npm test', { stdio: 'pipe' });
      checks.tests = true;
    } catch { checks.tests = false; }

    try {
      execSync('npm run build', { stdio: 'pipe' });
      checks.build = true;
    } catch { checks.build = false; }

    return checks;
  }

  async runOptimization() {
    try {
      const res = await fetch('http://localhost:3000/api/system/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'optimize' }),
      });
      return await res.json();
    } catch (error) {
      console.error('Optimization failed:', error);
      return null;
    }
  }

  async analyze() {
    try {
      const res = await fetch('http://localhost:3000/api/system/health');
      return await res.json();
    } catch (error) {
      console.error('Analysis failed:', error);
      return null;
    }
  }

  async runCycle() {
    console.log('[Self-Healing] Starting maintenance cycle...');
    
    const health = await this.healthCheck();
    if (!Object.values(health).every(v => v)) {
      console.log('[Self-Healing] Issues detected, running optimization...');
      const result = await this.runOptimization();
      console.log('[Self-Healing] Cleanup result:', result);
    }

    const analysis = await this.analyze();
    if (analysis?.recommendations?.length > 0) {
      console.log('[Self-Healing] Recommendations:', analysis.recommendations);
    }
  }
}

// Run on schedule
const system = new SelfHealingSystem();
system.runCycle().catch(console.error);
setInterval(() => system.runCycle().catch(console.error), 3600000); // Every hour
```

## Cost Optimization Recommendations

Add to `src/app/api/system/health/route.ts`:

```typescript
const costRecommendations: string[] = [];

// Database optimization
const dbSize = await prisma.$queryRaw`SELECT pg_database_size('your_database')`;
if (dbSize[0].pg_database_size > 1073741824) { // 1GB
  costRecommendations.push('Database exceeds 1GB. Consider archiving old data.');
}

// Storage optimization
const expiredSessions = await prisma.session.count({ where: { expiresAt: { lt: now } } });
if (expiredSessions > 10000) {
  costRecommendations.push(`${expiredSessions} expired sessions to clean up.`);
}

// API cost optimization
const apiCalls = await prisma.apiCallLog.count({ where: { createdAt: { gte: dayAgo } } });
if (apiCalls > 100000) {
  costRecommendations.push('High API call volume. Consider caching.');
}
```
