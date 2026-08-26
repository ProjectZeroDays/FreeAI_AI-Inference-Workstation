---
name: visitor-analytics-ai
description: Collect and analyze visitor data including user info, browser, OS, IP, location, impressions, and navigation paths. Use when building analytics dashboards, visitor tracking systems, AI-powered recommendations, or CRM integrations that need user behavior data. Triggers on: "track visitors", "collect user data", "analytics dashboard", "visitor insights", "AI recommendations based on traffic", "CRM visitor data", "user behavior tracking", "navigation analytics".
license: Complete terms in LICENSE.txt
---

# Visitor Analytics & AI Recommendations

This skill provides a complete system for collecting visitor data, analyzing behavior patterns, and generating AI-powered recommendations for the admin dashboard.

## Database Schema

Add to `prisma/schema.prisma`:

```prisma
model VisitorSession {
  @@map("visitor_sessions")
  id            String   @id @default(uuid()) @db.Uuid
  sessionId     String   @unique @db.Text
  userId        String?  @db.Uuid
  ip            String?  @db.Text
  userAgent     String?  @db.Text
  browser       String?  @db.Text
  os            String?  @db.Text
  device        String?  @db.Text
  country       String?  @db.Text
  region        String?  @db.Text
  city          String?  @db.Text
  referrer      String?  @db.Text
  landingPage   String?  @db.Text
  duration      Int?     @db.Int
  pagesViewed   Int      @default(0)
  impressions   Json     @default("[]")
  createdAt     DateTime @default(now()) @db.Timestamptz
  updatedAt     DateTime @updatedAt @db.Timestamptz
  user          User?    @relation("VisitorSessions", fields: [userId], references: [id], onDelete: SetNull)

  @@index([sessionId], map: "VisitorSession_sessionId_idx")
  @@index([userId], map: "VisitorSession_userId_idx")
  @@index([createdAt], map: "VisitorSession_createdAt_idx")
}

model PageImpression {
  @@map("page_impressions")
  id           String   @id @default(uuid()) @db.Uuid
  sessionId    String   @db.Uuid
  page         String   @db.Text
  pageTitle    String?  @db.Text
  timestamp    DateTime @default(now()) @db.Timestamptz
  duration     Int?     @db.Int
  session      VisitorSession @relation(fields: [sessionId], references: [id], onDelete: Cascade)

  @@index([sessionId], map: "PageImpression_sessionId_idx")
  @@index([page], map: "PageImpression_page_idx")
  @@index([timestamp], map: "PageImpression_timestamp_idx")
}

model AIRecommendation {
  @@map("ai_recommendations")
  id          String   @id @default(uuid()) @db.Uuid
  type        String   @db.Text
  priority    String   @default("medium") @db.Text
  title       String   @db.Text
  description String   @db.Text
  action      String?  @db.Text
  isResolved  Boolean  @default(false)
  createdBy   String   @default("AI_SYSTEM") @db.Text
  createdAt   DateTime @default(now()) @db.Timestamptz
  updatedAt   DateTime @updatedAt @db.Timestamptz

  @@index([type], map: "AIRecommendation_type_idx")
  @@index([isResolved], map: "AIRecommendation_isResolved_idx")
  @@index([createdAt], map: "AIRecommendation_createdAt_idx")
}
```

## Visitor Tracking Middleware

Create `src/middleware.ts`:

```typescript
import { NextRequest, NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
  const response = NextResponse.next();
  
  // Generate session ID if not exists
  const sessionId = request.cookies.get('sessions_id')?.value || crypto.randomUUID();
  response.cookies.set('sessions_id', sessionId, { httpOnly: true, sameSite: 'lax' });
  
  // Store IP and referrer
  const ip = request.headers.get('x-forwarded-for')?.split(',')[0].trim() || 'unknown';
  const referrer = request.headers.get('referer') || null;
  const userAgent = request.headers.get('user-agent') || null;
  
  // Store in response headers for API consumption
  response.headers.set('x-session-id', sessionId);
  response.headers.set('x-ip', ip);
  response.headers.set('x-ua', userAgent || '');
  response.headers.set('x-referrer', referrer || '');
  
  return response;
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
```

## Visitor Tracking API

Create `src/app/api/track/route.ts`:

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { geolocation } from '@vercel/edge';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, page, pageTitle, duration } = body;
    const sessionId = request.headers.get('x-session-id');
    const ip = request.headers.get('x-ip');
    const userAgent = request.headers.get('x-ua');
    const referrer = request.headers.get('x-referrer');

    if (!sessionId) {
      return NextResponse.json({ error: 'Session ID required' }, { status: 400 });
    }

    // Parse user agent
    const browser = parseBrowser(userAgent);
    const os = parseOS(userAgent);
    const device = parseDevice(userAgent);

    // Get location from IP
    const location = await getLocation(ip);

    let session = await prisma.visitorSession.findUnique({ where: { sessionId } });

    if (!session) {
      session = await prisma.visitorSession.create({
        data: {
          sessionId,
          ip,
          userAgent,
          browser,
          os,
          device,
          country: location?.country,
          region: location?.region,
          city: location?.city,
          referrer,
          landingPage: page,
        },
      });
    } else {
      await prisma.visitorSession.update({
        where: { sessionId },
        data: {
          updatedAt: new Date(),
          pagesViewed: { increment: 1 },
        },
      });
    }

    // Record page impression
    await prisma.pageImpression.create({
      data: {
        sessionId,
        page,
        pageTitle,
        duration,
      },
    });

    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

function parseBrowser(ua: string | null): string {
  if (!ua) return 'Unknown';
  if (ua.includes('Firefox')) return 'Firefox';
  if (ua.includes('Chrome')) return 'Chrome';
  if (ua.includes('Safari')) return 'Safari';
  if (ua.includes('Edge')) return 'Edge';
  return 'Other';
}

function parseOS(ua: string | null): string {
  if (!ua) return 'Unknown';
  if (ua.includes('Windows')) return 'Windows';
  if (ua.includes('Mac OS')) return 'macOS';
  if (ua.includes('Linux')) return 'Linux';
  if (ua.includes('Android')) return 'Android';
  if (ua.includes('iOS') || ua.includes('iPhone')) return 'iOS';
  return 'Other';
}

function parseDevice(ua: string | null): string {
  if (!ua) return 'Desktop';
  if (ua.includes('Mobile')) return 'Mobile';
  if (ua.includes('Tablet')) return 'Tablet';
  return 'Desktop';
}

async function getLocation(ip: string | null) {
  if (!ip || ip === 'unknown' || ip.startsWith('127.') || ip.startsWith('192.168')) {
    return null;
  }
  try {
    const res = await fetch(`https://api.ipgeolocation.io/ipgeo?apiKey=${process.env.IP_GEOLOCATION_API_KEY}&ip=${ip}`);
    return await res.json();
  } catch {
    return null;
  }
}
```

## Visitor Analytics API

Create `src/app/api/analytics/visitors/route.ts`:

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { withAuth, withRole, sendResponse, sendError } from '@/lib/middleware';

export const GET = withAuth(withRole(['ADMIN'])(async (req: NextRequest, res: NextResponse) => {
  const { searchParams } = new URL(req.url);
  const days = parseInt(searchParams.get('days') || '7');
  const startDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000);

  const [
    totalSessions, uniqueVisitors, returningVisitors,
    topPages, topReferrers, trafficByDevice, trafficByBrowser,
    trafficByOS, trafficByCountry, avgSessionDuration,
  ] = await Promise.all([
    prisma.visitorSession.count({ where: { createdAt: { gte: startDate } } }),
    prisma.visitorSession.count({ where: { createdAt: { gte: startDate } }, distinct: ['sessionId'] }),
    prisma.visitorSession.count({ where: { createdAt: { gte: startDate }, userId: { not: null } } }),
    prisma.pageImpression.groupBy({ by: ['page'], _count: { _all: true }, orderBy: { _count: { _all: 'desc' } }, take: 10, where: { timestamp: { gte: startDate } } }),
    prisma.visitorSession.groupBy({ by: ['referrer'], _count: { _all: true }, orderBy: { _count: { _all: 'desc' } }, take: 10, where: { createdAt: { gte: startDate } } }),
    prisma.visitorSession.groupBy({ by: ['device'], _count: { _all: true }, orderBy: { _count: { _all: 'desc' } }, where: { createdAt: { gte: startDate } } }),
    prisma.visitorSession.groupBy({ by: ['browser'], _count: { _all: true }, orderBy: { _count: { _all: 'desc' } }, where: { createdAt: { gte: startDate } } }),
    prisma.visitorSession.groupBy({ by: ['os'], _count: { _all: true }, orderBy: { _count: { _all: 'desc' } }, where: { createdAt: { gte: startDate } } }),
    prisma.visitorSession.groupBy({ by: ['country'], _count: { _all: true }, orderBy: { _count: { _all: 'desc' } }, take: 10, where: { createdAt: { gte: startDate }, country: { not: null } } }),
    prisma.visitorSession.aggregate({ _avg: { duration: true }, where: { createdAt: { gte: startDate } } }),
  ]);

  return sendResponse(res, {
    totalSessions,
    uniqueVisitors,
    returningVisitors,
    topPages,
    topReferrers,
    trafficByDevice,
    trafficByBrowser,
    trafficByOS,
    trafficByCountry,
    avgSessionDuration: avgSessionDuration._avg.duration || 0,
  });
}));
```

## AI Recommendations Engine

Create `src/app/api/analytics/recommendations/route.ts`:

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { withAuth, withRole, sendResponse, sendError } from '@/lib/middleware';

export const GET = withAuth(withRole(['ADMIN'])(async (req: NextRequest, res: NextResponse) => {
  const now = new Date();
  const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
  const dayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);

  const [
    newUsersWeek, newUsersToday,
    totalBookings, bookingsToday,
    totalTherapists, activeTherapists,
    revenueWeek, revenueToday,
    pendingVerifications,
    highBouncePages,
  ] = await Promise.all([
    prisma.user.count({ where: { createdAt: { gte: weekAgo } } }),
    prisma.user.count({ where: { createdAt: { gte: dayAgo } } }),
    prisma.booking.count({ where: { createdAt: { gte: weekAgo } } }),
    prisma.booking.count({ where: { createdAt: { gte: dayAgo } } }),
    prisma.therapistProfile.count(),
    prisma.therapistProfile.count({ where: { isApproved: true, subscriptionActive: true } }),
    prisma.payment.aggregate({ _sum: { amount: true }, where: { status: 'COMPLETED', createdAt: { gte: weekAgo } } }),
    prisma.payment.aggregate({ _sum: { amount: true }, where: { status: 'COMPLETED', createdAt: { gte: dayAgo } } }),
    prisma.verificationDoc.count({ where: { status: 'PENDING' } }),
    prisma.pageImpression.groupBy({ by: ['page'], _count: { _all: true }, having: { _count: { _all: { gt: 100 } } }, take: 5, where: { timestamp: { gte: weekAgo } } }),
  ]);

  const recommendations: Array<{ type: string; priority: string; title: string; description: string; action: string }> = [];

  // User growth recommendations
  if (newUsersToday === 0) {
    recommendations.push({
      type: 'growth',
      priority: 'high',
      title: 'No New Users Today',
      description: 'Zero new user registrations today. Check marketing channels and campaign status.',
      action: '/admin/analytics?tab=marketing',
    });
  }
  if (newUsersWeek < 10) {
    recommendations.push({
      type: 'growth',
      priority: 'medium',
      title: 'Low User Growth This Week',
      description: `Only ${newUsersWeek} new users this week. Consider increasing marketing spend or optimizing SEO.`,
      action: '/admin/analytics?tab=marketing',
    });
  }

  // Booking recommendations
  if (bookingsToday === 0 && activeTherapists > 0) {
    recommendations.push({
      type: 'bookings',
      priority: 'high',
      title: 'No Bookings Despite Active Therapists',
      description: `${activeTherapists} active therapists but zero bookings today. Check search visibility and therapist profiles.`,
      action: '/admin/therapists',
    });
  }
  if (bookingsToday < activeTherapists * 0.1) {
    recommendations.push({
      type: 'bookings',
      priority: 'medium',
      title: 'Low Booking Rate',
      description: 'Booking rate is below 10% of active therapists. Consider promotional offers or featured placements.',
      action: '/admin/therapists',
    });
  }

  // Revenue recommendations
  const revenueGrowth = revenueToday / (revenueWeek / 7);
  if (revenueGrowth < 0.8) {
    recommendations.push({
      type: 'revenue',
      priority: 'high',
      title: 'Revenue Decline Detected',
      description: `Daily revenue is ${((1 - revenueGrowth) * 100).toFixed(0)}% below weekly average. Investigate payment issues or checkout flow.`,
      action: '/admin/analytics?tab=revenue',
    });
  }

  // Verification backlog
  if (pendingVerifications > 20) {
    recommendations.push({
      type: 'operations',
      priority: 'high',
      title: 'High Verification Backlog',
      description: `${pendingVerifications} pending verifications. Delays may reduce therapist supply.`,
      action: '/admin/verifications',
    });
  }

  // Store recommendations
  for (const rec of recommendations) {
    await prisma.aIRecommendation.create({
      data: {
        ...rec,
        createdBy: 'AI_SYSTEM',
      },
    });
  }

  return sendResponse(res, { recommendations, stats: { newUsersWeek, newUsersToday, bookingsToday, revenueToday } });
}));
```

## Admin Analytics Dashboard

Create `src/app/admin/analytics/page.tsx`:

```tsx
'use client';
import { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function AnalyticsPage() {
  const [visitors, setVisitors] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetch('/api/analytics/visitors?days=30')
      .then(r => r.json())
      .then(data => setVisitors(data.data))
      .catch(console.error);

    fetch('/api/analytics/recommendations')
      .then(r => r.json())
      .then(data => setRecommendations(data.data?.recommendations || []))
      .catch(console.error);
  }, []);

  const COLORS = ['#7C3AED', '#06B6D4', '#10B981', '#F59E0B', '#EF4444'];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">Analytics & Insights</h1>

      {/* Recommendations Alert */}
      {recommendations.length > 0 && (
        <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4">
          <h3 className="text-amber-400 font-semibold mb-2">AI Recommendations</h3>
          {recommendations.map((rec, i) => (
            <a key={i} href={rec.action} className="block p-3 bg-surface-900 rounded-lg mb-2 hover:bg-surface-800 transition-colors">
              <div className="flex items-center justify-between">
                <span className="text-white font-medium">{rec.title}</span>
                <span className={`px-2 py-0.5 rounded-full text-xs ${
                  rec.priority === 'high' ? 'bg-red-500/20 text-red-400' : 'bg-amber-500/20 text-amber-400'
                }`}>{rec.priority}</span>
              </div>
              <p className="text-surface-400 text-sm mt-1">{rec.description}</p>
            </a>
          ))}
        </div>
      )}

      {/* Stats Cards */}
      {visitors && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-surface-900 rounded-xl p-4 border border-surface-800">
            <p className="text-surface-400 text-sm">Total Sessions</p>
            <p className="text-2xl font-bold text-white">{visitors.totalSessions}</p>
          </div>
          <div className="bg-surface-900 rounded-xl p-4 border border-surface-800">
            <p className="text-surface-400 text-sm">Unique Visitors</p>
            <p className="text-2xl font-bold text-white">{visitors.uniqueVisitors}</p>
          </div>
          <div className="bg-surface-900 rounded-xl p-4 border border-surface-800">
            <p className="text-surface-400 text-sm">Avg Duration</p>
            <p className="text-2xl font-bold text-white">{Math.round(visitors.avgSessionDuration)}s</p>
          </div>
          <div className="bg-surface-900 rounded-xl p-4 border border-surface-800">
            <p className="text-surface-400 text-sm">Returning</p>
            <p className="text-2xl font-bold text-white">{visitors.returningVisitors}</p>
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-surface-900 rounded-xl p-6 border border-surface-800">
          <h3 className="text-white font-semibold mb-4">Traffic by Device</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={visitors?.trafficByDevice || []} dataKey="_count._all" nameKey="device" cx="50%" cy="50%" outerRadius={80}>
                {visitors?.trafficByDevice?.map((_: any, i: number) => (
                  <Cell key={`cell-${i}`} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-surface-900 rounded-xl p-6 border border-surface-800">
          <h3 className="text-white font-semibold mb-4">Top Pages</h3>
          <div className="space-y-2">
            {(visitors?.topPages || []).slice(0, 5).map((p: any, i: number) => (
              <div key={i} className="flex justify-between text-sm">
                <span className="text-surface-300">{p.page}</span>
                <span className="text-white font-medium">{p._count._all}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
```

## Frontend Tracking Component

Create `src/components/VisitorTracker.tsx`:

```tsx
'use client';
import { useEffect } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';

export default function VisitorTracker() {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    const trackPageView = async () => {
      try {
        await fetch('/api/track', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action: 'pageview',
            page: pathname,
            pageTitle: document.title,
            timestamp: new Date().toISOString(),
          }),
        });
      } catch (error) {
        console.error('Tracking failed:', error);
      }
    };

    trackPageView();
  }, [pathname, searchParams]);

  return null;
}
```

Add to root layout:
```tsx
// src/app/layout.tsx
import VisitorTracker from '@/components/VisitorTracker';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {children}
        <VisitorTracker />
      </body>
    </html>
  );
}
```
