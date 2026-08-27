---
name: test-driven-development
description: Test-driven development workflows, test-first coding, red-green-refactor cycle, mocking patterns, test organization, and coverage strategies. Use when the user asks about writing tests first, TDD methodology, unit testing, integration testing, mocking/stubbing, or test architecture.
---

# Test-Driven Development

## Red-Green-Refactor Cycle

1. **Red** — Write a failing test that defines desired behavior
2. **Green** — Write minimum code to make the test pass
3. **Refactor** — Clean up code while keeping tests green

## Writing Good Tests

### Arrange-Act-Assert
```typescript
test("calculates total with tax", () => {
  // Arrange
  const items = [{ price: 10 }, { price: 20 }];
  const taxRate = 0.1;

  // Act
  const total = calculateTotal(items, taxRate);

  // Assert
  expect(total).toBe(33);
});
```

### Test Naming Convention
```typescript
// Pattern: should/it [action] [expected result]
it("should return 404 when user does not exist")
it("should throw ValidationError for invalid email")
it("should send welcome email after registration")
```

## TDD Kata: String Calculator

```python
# Step 1: Empty string returns 0
def test_empty_string_returns_zero():
    assert add("") == 0

def add(numbers: str) -> int:
    return 0

# Step 2: Single number returns itself
def test_single_number():
    assert add("5") == 5

def add(numbers: str) -> int:
    if not numbers:
        return 0
    return int(numbers)

# Step 3: Two numbers comma-separated
def test_two_numbers():
    assert add("1,2") == 3

def add(numbers: str) -> int:
    if not numbers:
        return 0
    return sum(int(n) for n in numbers.split(","))
```

## Mocking Patterns

### Python (pytest)
```python
from unittest.mock import Mock, patch

def test_send_email():
    mock_smtp = Mock()
    mock_smtp.sendmail.return_value = {}
    
    service = EmailService(mock_smtp)
    service.send("user@test.com", "Hello")
    
    mock_smtp.sendmail.assert_called_once_with(
        "noreply@app.com", "user@test.com", "Hello"
    )

@patch("services.email.smtp.SMTP")
def test_with_real_smtp(mock_smtp_class):
    mock_instance = Mock()
    mock_smtp_class.return_value = mock_instance
    
    service = EmailService()
    service.send("user@test.com", "Hello")
    
    mock_instance.starttls.assert_called_once()
```

### TypeScript (Vitest/Jest)
```typescript
import { vi, describe, it, expect } from 'vitest';

describe("UserService", () => {
  it("creates user and sends welcome email", async () => {
    const mockDb = { insert: vi.fn().mockResolvedValue({ id: 1 }) };
    const mockMailer = { send: vi.fn().mockResolvedValue({}) };
    
    const service = new UserService(mockDb, mockMailer);
    const user = await service.create({ name: "Alice", email: "a@b.com" });
    
    expect(mockDb.insert).toHaveBeenCalledWith({
      name: "Alice",
      email: "a@b.com"
    });
    expect(mockMailer.send).toHaveBeenCalledWith(
      expect.objectContaining({ to: "a@b.com" })
    );
    expect(user.id).toBe(1);
  });
});
```

## Test Organization

```
src/
  services/
    user.service.ts
  __tests__/
    user.service.test.ts    # unit tests
  __tests__/
    integration/
      user.api.test.ts      # integration tests
```

### Naming Convention
```
*.test.ts    — unit tests
*.spec.ts    — unit tests (alternative)
*.api.test.ts — API/integration tests
*.e2e.test.ts — end-to-end tests
```

## Fixture Patterns

```python
import pytest

@pytest.fixture
def db_session():
    session = create_test_session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def sample_user(db_session):
    user = User(name="Test", email="test@example.com")
    db_session.add(user)
    db_session.commit()
    return user

def test_get_user(db_session, sample_user):
    result = db_session.query(User).get(sample_user.id)
    assert result.name == "Test"
```

## Testing Edge Cases

```python
def test_divide_by_zero_raises():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_returns_none_for_missing_key():
    result = get_value({}, "missing")
    assert result is None

def test_handles_empty_list():
    result = calculate_average([])
    assert result == 0
```

## Coverage Strategy

- Aim for high coverage on business logic (80%+)
- Don't chase 100% — focus on critical paths
- Test behavior, not implementation details
- One assertion per concept (multiple assertions OK if testing one behavior)

## When NOT to TDD

- Exploratory/spike code — figure out approach first
- UI/visual work — screenshot testing instead
- Simple configuration — not worth the overhead
- Third-party integrations — mock at boundary, test integration separately
