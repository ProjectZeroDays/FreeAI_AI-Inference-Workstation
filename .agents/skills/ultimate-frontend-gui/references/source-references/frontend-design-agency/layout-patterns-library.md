# Layout Patterns Library

> **Umsetzungshilfe, keine Standardlösung.**
> Diese Datei ist nicht normativ. Sie darf keine Produktentscheidung vorwegnehmen und keine definierte visuelle These überschreiben.
> Layout-Patterns dienen als Strukturreferenz, nicht als fertige Lösung. Passe sie an die definierte Informationsarchitektur, visuelle These und Produktlogik an, statt sie 1:1 zu übernehmen.

Wiederverwendbare Layout-Patterns für Web-Apps.

## 1. App Shell

### Sidebar Navigation

```tsx
function AppShell() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen bg-canvas">
      {/* Sidebar - Desktop fixed, Mobile drawer */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-64 bg-surface border-r transform transition-transform lg:static lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <SidebarContent />
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>

      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
}
```

### Top Navigation

```tsx
function TopNavShell() {
  return (
    <div className="min-h-screen bg-canvas">
      <header className="sticky top-0 z-50 bg-surface border-b">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <Logo />
          <nav className="hidden md:flex items-center gap-6">
            <NavLinks />
          </nav>
          <UserMenu />
        </div>
      </header>
      <main className="container mx-auto px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
```

## 2. Dashboard Layouts

### Standard Dashboard

```tsx
function StandardDashboard() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="Dashboard"
        actions={<Button>Export</Button>}
      />

      {/* KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard title="Users" value="12,345" change="+12%" />
        <KpiCard title="Revenue" value="€45.2k" change="+8%" />
        <KpiCard title="Conversion" value="3.2%" change="-2%" />
        <KpiCard title="Active Now" value="42" />
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ChartCard title="Performance" />
        </div>
        <div>
          <RecentActivity />
        </div>
      </div>

      {/* Table Section */}
      <DataTableCard title="Recent Orders" />
    </div>
  );
}
```

### Analytics Dashboard

```tsx
function AnalyticsDashboard() {
  return (
    <div className="space-y-6">
      {/* Controls Row */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <h1 className="text-2xl font-bold">Analytics</h1>
        <div className="flex items-center gap-2">
          <DateRangePicker />
          <Button variant="secondary">Export</Button>
        </div>
      </div>

      {/* Main Chart */}
      <Card className="p-6">
        <LineChart height={400} />
      </Card>

      {/* Secondary Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card className="p-4"><BarChart /></Card>
        <Card className="p-4"><PieChart /></Card>
        <Card className="p-4"><StatsList /></Card>
      </div>
    </div>
  );
}
```

## 3. Form Layouts

### Single Column Form

```tsx
function SingleColumnForm() {
  return (
    <div className="max-w-xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Create Account</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input label="Full Name" required />
          <Input label="Email" type="email" required />
          <Input label="Password" type="password" required />
          <div className="pt-4">
            <Button className="w-full">Create Account</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
```

### Two Column Form

```tsx
function TwoColumnForm() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Company Settings</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <h3 className="font-medium">General</h3>
            <Input label="Company Name" />
            <Input label="Tax ID" />
            <Input label="Website" />
          </div>
          <div className="space-y-4">
            <h3 className="font-medium">Address</h3>
            <Input label="Street" />
            <Input label="City" />
            <div className="grid grid-cols-2 gap-4">
              <Input label="ZIP" />
              <Input label="Country" />
            </div>
          </div>
        </div>
        <div className="mt-6 flex justify-end gap-3">
          <Button variant="ghost">Cancel</Button>
          <Button>Save Changes</Button>
        </div>
      </CardContent>
    </Card>
  );
}
```

### Sectioned Form

```tsx
function SectionedForm() {
  return (
    <div className="space-y-6">
      {/* Section 1 */}
      <Card>
        <CardHeader>
          <CardTitle>Profile Information</CardTitle>
          <p className="text-sm text-muted">Update your personal details</p>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input label="First Name" />
          <Input label="Last Name" />
          <Input label="Email" className="md:col-span-2" />
        </CardContent>
      </Card>

      {/* Section 2 */}
      <Card>
        <CardHeader>
          <CardTitle>Notifications</CardTitle>
          <p className="text-sm text-muted">Manage your email preferences</p>
        </CardHeader>
        <CardContent className="space-y-3">
          <Switch label="Marketing emails" />
          <Switch label="Product updates" />
          <Switch label="Security alerts" />
        </CardContent>
      </Card>

      {/* Sticky Footer */}
      <div className="sticky bottom-0 bg-surface border-t p-4 flex justify-end gap-3">
        <Button variant="ghost">Reset</Button>
        <Button>Save All Changes</Button>
      </div>
    </div>
  );
}
```

## 4. List Layouts

### Standard List

```tsx
function StandardList({ items }) {
  return (
    <div className="divide-y">
      {items.map(item => (
        <div key={item.id} className="flex items-center justify-between py-4">
          <div className="flex items-center gap-4">
            <Avatar src={item.avatar} />
            <div>
              <p className="font-medium">{item.name}</p>
              <p className="text-sm text-muted">{item.email}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge>{item.role}</Badge>
            <DropdownMenu />
          </div>
        </div>
      ))}
    </div>
  );
}
```

### Card List (Mobile)

```tsx
function CardList({ items }) {
  return (
    <div className="grid grid-cols-1 gap-4 md:hidden">
      {items.map(item => (
        <Card key={item.id} className="p-4">
          <div className="flex items-start justify-between">
            <div>
              <h4 className="font-medium">{item.title}</h4>
              <p className="text-sm text-muted mt-1">{item.description}</p>
            </div>
            <StatusBadge status={item.status} />
          </div>
          <div className="mt-4 flex items-center justify-between text-sm text-muted">
            <span>{item.date}</span>
            <span>{item.amount}</span>
          </div>
        </Card>
      ))}
    </div>
  );
}
```

### Table + Cards Hybrid

```tsx
function HybridList({ items }) {
  return (
    <>
      {/* Desktop: Table */}
      <div className="hidden md:block">
        <DataTable data={items} />
      </div>
      {/* Mobile: Cards */}
      <div className="md:hidden">
        <CardList items={items} />
      </div>
    </>
  );
}
```

## 5. Detail Views

### Two-Panel Detail

```tsx
function DetailView({ data }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Main Info */}
      <div className="lg:col-span-2 space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>{data.title}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <DescriptionList data={data.fields} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <Timeline items={data.activity} />
          </CardContent>
        </Card>
      </div>

      {/* Sidebar Info */}
      <div className="space-y-6">
        <Card>
          <CardContent className="p-6 space-y-4">
            <div className="flex items-center gap-4">
              <Avatar src={data.assignee.avatar} className="h-12 w-12" />
              <div>
                <p className="font-medium">{data.assignee.name}</p>
                <p className="text-sm text-muted">Assignee</p>
              </div>
            </div>
            <Separator />
            <div className="space-y-3">
              <InfoRow label="Status" value={<StatusBadge status={data.status} />} />
              <InfoRow label="Due Date" value={formatDate(data.dueDate)} />
              <InfoRow label="Priority" value={<PriorityBadge priority={data.priority} />} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button className="w-full">Edit</Button>
            <Button variant="secondary" className="w-full">Duplicate</Button>
            <Button variant="danger" className="w-full">Delete</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

## 6. Marketing/Content Layouts

### Hero Section

```tsx
function HeroSection() {
  return (
    <section className="relative py-20 lg:py-32">
      <div className="container mx-auto px-4">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <Badge variant="primary">New Feature</Badge>
            <h1 className="text-4xl lg:text-6xl font-bold leading-tight">
              Headline that converts visitors
            </h1>
            <p className="text-lg text-muted max-w-lg">
              Subtext explaining the value proposition in clear,
              benefit-focused language.
            </p>
            <div className="flex flex-col sm:flex-row gap-3">
              <Button size="lg">Get Started</Button>
              <Button variant="secondary" size="lg">Learn More</Button>
            </div>
          </div>
          <div className="relative">
            <HeroImage />
          </div>
        </div>
      </div>
    </section>
  );
}
```

### Feature Grid

```tsx
function FeatureGrid() {
  const features = [
    { icon: Zap, title: "Fast", description: "..." },
    { icon: Shield, title: "Secure", description: "..." },
    { icon: Scale, title: "Scalable", description: "..." },
  ];

  return (
    <section className="py-20 bg-surface-subtle">
      <div className="container mx-auto px-4">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <h2 className="text-3xl font-bold mb-4">Why Choose Us</h2>
          <p className="text-muted">Features that make the difference</p>
        </div>
        <div className="grid md:grid-cols-3 gap-8">
          {features.map(feature => (
            <div key={feature.title} className="text-center">
              <feature.icon className="h-12 w-12 mx-auto mb-4 text-primary" />
              <h3 className="font-semibold mb-2">{feature.title}</h3>
              <p className="text-muted text-sm">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
```

## Pattern-Checkliste

- [ ] Layout für alle Breakpoints getestet?
- [ ] Content-Hierarchie klar?
- [ ] White-Raum angemessen?
- [ ] Konsistente Abstände?
- [ ] Mobile Touch-Targets ≥ 44px?
- [ ] Responsive Images optimiert?
- [ ] Loading States berücksichtigt?
- [ ] Empty States definiert?
