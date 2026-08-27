# Component Template (React + TypeScript + Tailwind)

> **Umsetzungshilfe, keine Standardlösung.**
> Übernimm Struktur oder Patterns nur, wenn sie zur definierten Produktlogik, visuellen These und Informationsarchitektur passen. Passe Varianten, Klassen und Tokens an die Designrichtung an.

## Basis-Template

```tsx
import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

// ============================================
// Button Component
// ============================================

const buttonVariants = cva(
  // Base styles
  'inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary-hover active:bg-primary-active',
        secondary: 'bg-surface border border-border-default hover:bg-surface-subtle',
        ghost: 'hover:bg-surface-subtle',
        danger: 'bg-danger text-white hover:bg-danger-hover',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-8 px-3 text-xs',
        lg: 'h-12 px-6 text-base',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  isLoading?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, isLoading, children, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button';
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        disabled={props.disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <>
            <LoadingIcon className="mr-2 h-4 w-4 animate-spin" />
            {children}
          </>
        ) : (
          children
        )}
      </Comp>
    );
  }
);
Button.displayName = 'Button';

// ============================================
// Card Component
// ============================================

const Card = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      'rounded-lg border bg-surface shadow-sm transition-shadow hover:shadow-md',
      className
    )}
    {...props}
  />
));
Card.displayName = 'Card';

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('flex flex-col space-y-1.5 p-6', className)} {...props} />
));
CardHeader.displayName = 'CardHeader';

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn('text-2xl font-semibold leading-none tracking-tight', className)}
    {...props}
  />
));
CardTitle.displayName = 'CardTitle';

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('p-6 pt-0', className)} {...props} />
));
CardContent.displayName = 'CardContent';

// ============================================
// Input Component
// ============================================

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string;
  label?: string;
  helperText?: string;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, error, label, helperText, ...props }, ref) => {
    return (
      <div className="space-y-2">
        {label && (
          <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
            {label}
          </label>
        )}
        <input
          type={type}
          className={cn(
            'flex h-10 w-full rounded-md border border-border-default bg-surface px-3 py-2 text-sm placeholder:text-text-placeholder focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:cursor-not-allowed disabled:opacity-50',
            error && 'border-danger focus-visible:ring-danger',
            className
          )}
          ref={ref}
          {...props}
        />
        {helperText && !error && (
          <p className="text-xs text-text-muted">{helperText}</p>
        )}
        {error && (
          <p className="text-xs text-danger">{error}</p>
        )}
      </div>
    );
  }
);
Input.displayName = 'Input';

// ============================================
// Badge Component
// ============================================

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-primary text-primary-foreground',
        secondary: 'border-transparent bg-surface-subtle text-text-default',
        success: 'border-transparent bg-success text-white',
        warning: 'border-transparent bg-warning text-white',
        danger: 'border-transparent bg-danger text-white',
        outline: 'text-text-default border-border-default',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

// ============================================
// Empty State Component
// ============================================

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center">
      {icon && (
        <div className="mb-4 text-text-muted">{icon}</div>
      )}
      <h3 className="mb-2 text-lg font-semibold text-text-strong">{title}</h3>
      {description && (
        <p className="mb-4 max-w-sm text-sm text-text-muted">{description}</p>
      )}
      {action}
    </div>
  );
}

// ============================================
// Status Indicator Component
// ============================================

interface StatusIndicatorProps {
  status: 'online' | 'offline' | 'busy' | 'away' | 'loading';
  label?: string;
  showDot?: boolean;
}

const statusColors = {
  online: 'bg-success',
  offline: 'bg-text-muted',
  busy: 'bg-danger',
  away: 'bg-warning',
  loading: 'bg-primary animate-pulse',
};

function StatusIndicator({ status, label, showDot = true }: StatusIndicatorProps) {
  return (
    <div className="flex items-center gap-2">
      {showDot && (
        <span className={cn('h-2.5 w-2.5 rounded-full', statusColors[status])} />
      )}
      {label && (
        <span className="text-sm text-text-muted">{label}</span>
      )}
    </div>
  );
}

// ============================================
// Page Header Component
// ============================================

interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: React.ReactNode;
}

function PageHeader({ title, description, actions }: PageHeaderProps) {
  return (
    <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-text-strong">{title}</h1>
        {description && (
          <p className="mt-2 text-text-muted">{description}</p>
        )}
      </div>
      {actions && (
        <div className="flex items-center gap-3">{actions}</div>
      )}
    </div>
  );
}

// ============================================
// Exports
// ============================================

export {
  Button,
  buttonVariants,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Input,
  Badge,
  badgeVariants,
  EmptyState,
  StatusIndicator,
  PageHeader,
};
```

## Verwendung

```tsx
// Button mit Varianten
<Button>Default</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="danger">Löschen</Button>
<Button size="sm">Klein</Button>
<Button isLoading>Lädt...</Button>

// Card
<Card>
  <CardHeader>
    <CardTitle>Titel</CardTitle>
  </CardHeader>
  <CardContent>Inhalt</CardContent>
</Card>

// Input mit Label und Fehler
<Input
  label="E-Mail"
  type="email"
  placeholder="name@beispiel.de"
  helperText="Wir senden eine Bestätigung"
  error={errors.email}
/>

// Badge
<Badge>Neu</Badge>
<Badge variant="success">Aktiv</Badge>
<Badge variant="outline">Entwurf</Badge>

// Empty State
<EmptyState
  icon={<FolderOpen className="h-12 w-12" />}
  title="Keine Projekte"
  description="Erstelle dein erstes Projekt, um loszulegen."
  action={<Button>Projekt erstellen</Button>}
/>

// Page Header
<PageHeader
  title="Dashboard"
  description="Übersicht deiner Aktivitäten"
  actions={<Button>Neuer Bericht</Button>}
/>
```

## Checkliste für neue Komponenten

- [ ] Props-Interface definiert
- [ ] Varianten mit cva (wenn nötig)
- [ ] ForwardRef implementiert
- [ ] displayName gesetzt
- [ ] Zustände: default, hover, focus, disabled, loading
- [ ] TypeScript-Typen korrekt
- [ ] Barrierefreiheit (aria-*)
- [ ] Dokumentation/Kommentare
