---
name: error-handling
description: Error handling patterns, custom exceptions, error boundaries, retry strategies, and graceful degradation. Use when the user asks about implementing error handling, creating custom error classes, building error boundaries, retry logic, or graceful failure handling.
---

# Error Handling

## Custom Error Classes

```typescript
// Base application error
class AppError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 500,
    public isOperational: boolean = true
  ) {
    super(message);
    this.name = this.constructor.name;
    Error.captureStackTrace(this, this.constructor);
  }
}

class ValidationError extends AppError {
  constructor(message: string, public fields: Record<string, string>) {
    super(message, 'VALIDATION_ERROR', 400);
  }
}

class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super(`${resource} with id ${id} not found`, 'NOT_FOUND', 404);
  }
}

class UnauthorizedError extends AppError {
  constructor(message = 'Authentication required') {
    super(message, 'UNAUTHORIZED', 401);
  }
}

class ConflictError extends AppError {
  constructor(message: string) {
    super(message, 'CONFLICT', 409);
  }
}
```

## Error Handler Middleware

```typescript
// Express error handler
function errorHandler(err: Error, req: Request, res: Response, next: NextFunction) {
  // Log error
  logger.error({
    message: err.message,
    stack: err.stack,
    requestId: req.id,
    path: req.path,
    method: req.method,
  });

  // Operational errors (expected)
  if (err instanceof AppError && err.isOperational) {
    return res.status(err.statusCode).json({
      error: {
        code: err.code,
        message: err.message,
        ...(err instanceof ValidationError && { fields: err.fields }),
      },
    });
  }

  // Programming errors (bugs)
  return res.status(500).json({
    error: {
      code: 'INTERNAL_ERROR',
      message: 'An unexpected error occurred',
    },
  });
}
```

## Python Error Handling

```python
from dataclasses import dataclass
from typing import Any

class AppError(Exception):
    def __init__(self, message: str, code: str, status_code: int = 500):
        super().__init__(message)
        self.code = code
        self.status_code = status_code

class ValidationError(AppError):
    def __init__(self, message: str, fields: dict[str, str] | None = None):
        super().__init__(message, 'VALIDATION_ERROR', 400)
        self.fields = fields or {}

class NotFoundError(AppError):
    def __init__(self, resource: str, identifier: str):
        super().__init__(f'{resource} {identifier} not found', 'NOT_FOUND', 404)

# Usage with context manager
from contextlib import contextmanager

@contextmanager
def handle_errors():
    try:
        yield
    except ValidationError as e:
        return {"error": {"code": e.code, "message": str(e), "fields": e.fields}}
    except AppError as e:
        return {"error": {"code": e.code, "message": str(e)}}
    except Exception as e:
        logger.exception("Unexpected error")
        return {"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}}
```

## Retry Pattern

```typescript
interface RetryOptions {
  maxAttempts: number;
  delay: number;
  backoff: 'linear' | 'exponential';
  retryOn?: (error: Error) => boolean;
}

async function withRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions
): Promise<T> {
  const { maxAttempts, delay, backoff, retryOn } = options;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      const shouldRetry =
        attempt < maxAttempts &&
        (!retryOn || retryOn(error as Error));

      if (!shouldRetry) throw error;

      const waitTime = backoff === 'exponential'
        ? delay * Math.pow(2, attempt - 1)
        : delay * attempt;

      console.log(`Attempt ${attempt} failed, retrying in ${waitTime}ms...`);
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }
  }

  throw new Error('Max attempts exceeded');
}

// Usage
const result = await withRetry(
  () => fetch('https://api.example.com/data'),
  {
    maxAttempts: 3,
    delay: 1000,
    backoff: 'exponential',
    retryOn: (error) => error instanceof TypeError,
  }
);
```

## Circuit Breaker

```typescript
class CircuitBreaker {
  private failures = 0;
  private lastFailure = 0;
  private state: 'closed' | 'open' | 'half-open' = 'closed';

  constructor(
    private threshold: number = 5,
    private resetTimeout: number = 60000
  ) {}

  async call<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === 'open') {
      if (Date.now() - this.lastFailure > this.resetTimeout) {
        this.state = 'half-open';
      } else {
        throw new Error('Circuit breaker is open');
      }
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  private onSuccess() {
    this.failures = 0;
    this.state = 'closed';
  }

  private onFailure() {
    this.failures++;
    this.lastFailure = Date.now();
    if (this.failures >= this.threshold) {
      this.state = 'open';
    }
  }
}
```

## Error Boundary (React)

```typescript
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div role="alert">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
```

## Result Type (No Exceptions)

```typescript
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

function ok<T>(value: T): Result<T, never> {
  return { ok: true, value };
}

function err<E>(error: E): Result<never, E> {
  return { ok: false, error };
}

// Usage
function divide(a: number, b: number): Result<number, string> {
  if (b === 0) return err('Division by zero');
  return ok(a / b);
}

const result = divide(10, 2);
if (result.ok) {
  console.log(result.value); // 5
} else {
  console.error(result.error); // "Division by zero"
}
```

## Best Practices

1. Distinguish operational vs programming errors
2. Always log errors with context
3. Use specific error types/codes
4. Don't swallow errors silently
5. Validate at boundaries
6. Implement retry with backoff for transient failures
7. Use circuit breakers for external services
8. Provide meaningful error messages
9. Handle errors at the appropriate level
10. Never expose internal errors to users
