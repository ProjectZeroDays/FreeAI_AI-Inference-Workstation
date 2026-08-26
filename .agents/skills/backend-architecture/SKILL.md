---
name: backend-architecture
description: Backend architecture patterns, service design, microservices, event-driven architecture, CQRS, and system design. Use when the user asks about designing backend systems, microservice boundaries, event sourcing, CQRS, API gateway patterns, or distributed system design.
---

# Backend Architecture

## Layered Architecture

```
┌─────────────────┐
│  Presentation   │  Controllers, routes, handlers
├─────────────────┤
│  Business Logic │  Services, domain logic
├─────────────────┤
│  Data Access    │  Repositories, ORM, queries
├─────────────────┤
│  Infrastructure │  Database, cache, external APIs
└─────────────────┘
```

### Express.js Example
```
routes/          → HTTP handling
services/        → Business logic
repositories/    → Data access
models/          → Domain entities
middleware/      → Cross-cutting concerns
```

## Repository Pattern

```python
from abc import ABC, abstractmethod

class UserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: str) -> User | None:
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        pass

class PostgresUserRepository(UserRepository):
    def __init__(self, session):
        self.session = session

    def find_by_id(self, user_id: str) -> User | None:
        row = self.session.query(UserModel).get(user_id)
        return self._to_domain(row) if row else None

    def save(self, user: User) -> User:
        model = self._to_model(user)
        self.session.add(model)
        self.session.commit()
        return user
```

## CQRS (Command Query Responsibility Segregation)

```
Commands (Write)          Queries (Read)
─────────────────        ─────────────────
CreateUserCommand         GetUserQuery
UpdateUserCommand         ListUsersQuery
DeleteUserCommand         SearchUsersQuery
        │                         │
        ▼                         ▼
   Write DB                  Read DB (optimized)
   (normalized)             (denormalized)
```

```python
# Command
class CreateUserHandler:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def handle(self, cmd: CreateUserCommand) -> User:
        user = User(name=cmd.name, email=cmd.email)
        return self.repo.save(user)

# Query
class GetUserHandler:
    def __init__(self, read_repo: UserReadRepository):
        self.read_repo = read_repo

    def handle(self, query: GetUserQuery) -> UserDTO:
        return self.read_repo.find_by_id(query.user_id)
```

## Event-Driven Architecture

```python
# Event definitions
from dataclasses import dataclass

@dataclass
class UserCreated:
    user_id: str
    email: str
    timestamp: datetime

@dataclass
class OrderPlaced:
    order_id: str
    user_id: str
    total: float

# Event bus
class EventBus:
    def __init__(self):
        self.handlers = {}

    def subscribe(self, event_type, handler):
        self.handlers.setdefault(event_type, []).append(handler)

    async def publish(self, event):
        for handler in self.handlers.get(type(event), []):
            await handler(event)

# Usage
event_bus = EventBus()

async def on_user_created(event: UserCreated):
    await send_welcome_email(event.email)

event_bus.subscribe(UserCreated, on_user_created)
```

## API Gateway Pattern

```yaml
# Routes through gateway
/api/v1/users/**     → user-service:3001
/api/v1/orders/**    → order-service:3002
/api/v1/products/**  → product-service:3003
/api/v1/auth/**      → auth-service:3000
```

### Gateway Responsibilities
- Request routing
- Authentication/authorization
- Rate limiting
- Request/response transformation
- API composition (aggregate multiple services)

## Circuit Breaker

```python
import circuitbreaker

class ExternalAPIFallback(Exception):
    pass

@circuitbreaker.circuit(failure_threshold=5, recovery_timeout=60)
def call_external_api(data):
    response = requests.post("https://api.external.com", json=data)
    response.raise_for_status()
    return response.json()

# Fallback
try:
    result = call_external_api(data)
except circuitbreaker.CircuitBreakerError:
    result = get_cached_result(data)
```

## Service Communication

### Synchronous (HTTP/gRPC)
```
Client → Service A → Service B → Database
         (calls B directly)
```

### Asynchronous (Message Queue)
```
Service A → Queue → Service B
                   → Service C
                   (independent consumers)
```

## Saga Pattern (Distributed Transactions)

```
Order Saga:
1. CreateOrder → success
2. ReserveInventory → success
3. ProcessPayment → FAIL
   → Compensate: CancelOrder
   → Compensate: ReleaseInventory
```

## Domain-Driven Design

```
src/
  domain/
    user/
      user.entity.ts
      user.repository.ts
      user.service.ts
    order/
      order.entity.ts
      order.repository.ts
      order.service.ts
  application/
    create-order.handler.ts
    get-user.handler.ts
  infrastructure/
    postgres/
      user.repository.impl.ts
    redis/
      cache.service.ts
```

## System Design Checklist

- [ ] Define clear service boundaries
- [ ] Identify data ownership per service
- [ ] Choose sync vs async communication
- [ ] Plan for failure (circuit breakers, retries)
- [ ] Design for observability (logs, metrics, traces)
- [ ] Consider data consistency model (strong vs eventual)
- [ ] Plan scaling strategy (horizontal vs vertical)
- [ ] Define API contracts upfront
- [ ] Implement health checks
- [ ] Plan database strategy (per-service DB vs shared)
